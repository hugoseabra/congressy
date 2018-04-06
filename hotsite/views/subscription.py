from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.views import generic

from gatheros_event.forms import PersonForm
from gatheros_subscription.models import FormConfig, Lot, \
    Subscription
from hotsite.views import SubscriptionFormMixin
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.tasks import create_pagarme_transaction
from survey.directors import SurveyDirector


class SubscriptionView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/subscription.html'
    form_class = PersonForm

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()
        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        # Se o já inscrito e porém, não há lotes pagos, não há o que
        # fazer aqui.
        # if self.is_subscribed() and self.has_paid_lots():
        #     return redirect(
        #         'public:hotsite-subscription-status',
        #         slug=self.event.slug
        #     )

        return response

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        required_fields = ['gender']

        has_paid_lots = self.has_paid_lots()

        if has_paid_lots or config.phone:
            required_fields.append('phone')

        if has_paid_lots or config.address_show:
            required_fields.append('street')
            required_fields.append('village')
            required_fields.append('zip_code')
            required_fields.append('city')

        if not has_paid_lots \
                and not config.address_show \
                and config.city is True:
            required_fields.append('city')

        if has_paid_lots or config.cpf_required:
            required_fields.append('cpf')

        if has_paid_lots or config.birth_date_required:
            required_fields.append('birth_date')

        for field_name in required_fields:
            form.setAsRequired(field_name)

        return form

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        survey_director = SurveyDirector(event=self.event,
                                         user=self.request.user)

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()

        if self.has_paid_lots():
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        cxt['config'] = config
        cxt['surveys'] = survey_director.get_forms()
        cxt['remove_preloader'] = True
        cxt['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

        return cxt

    def post(self, request, *args, **kwargs):
        """
        CONDIÇÃO 1: usuário não autenticado ou inscrições não disponíveis
            - retorna a página inicial

        CONDIÇÃO 2: dados inválidos
            - retorna a página de inscrição com devidas mensagens de erro(s)

        CONDIÇÃO 3: verificação de conta (nova ou usuáro ativo [já logou])
            - seta uma 'flag' da verficação para futuras condicionais

        CONDIÇÃO 4: usuário já inscrito
            - seta uma 'flag' da verficação para futuras condicionais

        CONDIÇÃO 5: inscrição gratuita
            - se inscrição não existe, cria inscrição
            - se inscrição já existe, edit inscrição
            - notifica usuário;
            - redireciona para página inicial;

        CONDIÇÃO 6: lote pago, ação proibido
            - verificação: não há lotes pagos e transação não permitida
            - redireciona usuário para página de inscrição com mensagem e erro

        CONDIÇÃO 7: lote pago, transação permitida
            - se inscrição não existe, cria inscrição
            - se inscrição já existe, edit inscrição
            - processa pagamento;
            - notifica usuário;
            - redireciona para página de status

        CONDIÇÂO 8: status da inscrição
            - verifica o tipo de lotes, caso não tenha lotes pagos, então a
              inscrição é confirmada
        CONDIÇÃO 9:
            - verifica se lote possui formulario(survey)
            - se possuir survey, pegar o querydict que vem do post, e tentar
                validar o survey.
            - caso não valide redireciona usuário para página de inscrição
              com mensagem e erro.
            - caso valide:
                - verificar se esse usuário já possui autoria deste survey.
                - caso exista, resgate e atualize.
                - caso não exista, crie.
        """
        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = True

        user = self.request.user

        # CONDIÇÃO 7
        # if self.has_paid_lots():
        #     allowed_transaction = request.POST.get(
        #         'allowed_transaction',
        #         False
        #     )
        #
        #     # CONDIÇÃO 6
        #     if allowed_transaction:
        #         request.session['allowed_transaction'] = allowed_transaction
        #         slug = kwargs.get('slug')
        #         return redirect('public:hotsite-subscription', slug=slug)

        # CONDIÇÃO 1
        if not user.is_authenticated or not self.subscription_enabled():
            return HttpResponseNotAllowed([])

        # CONDIÇÃO 2
        request.POST = request.POST.copy()

        def clear_string(field_name):
            if field_name not in request.POST:
                return

            value = request.POST.get(field_name)

            if not value:
                return ''

            value = value \
                .replace('.', '') \
                .replace('-', '') \
                .replace('/', '') \
                .replace('(', '') \
                .replace(')', '') \
                .replace(' ', '')

            request.POST[field_name] = value

        clear_string('cpf')
        clear_string('zip_code')
        clear_string('phone')
        clear_string('institution_cnpj')

        # Resgata e verifica lote se houver
        # È necessario resgatar ele para facilitar as validações dos
        # possiveis surveys que estão vinculados a ele
        if 'lot' in request.POST:
            lot_pk = self.request.POST.get('lot')
            lot_pk = int(lot_pk) if lot_pk else 0

            # Garante que o lote é do evento
            try:
                lot = self.event.lots.get(pk=int(lot_pk))
            except Lot.DoesNotExist:
                messages.error(request, "Lote inválido.")
                return self.render_to_response(context)

        else:
            # Inscrição simples
            lot = self.event.lots.first()

        form = self.get_form()

        # CONDIÇÃO 9
        """
            CONDIÇÃO 9:
            - verifica se lote possui formulario(survey)
            - se possuir survey, pegar o querydict que vem do post, e tentar 
            validar o survey.
            - caso não valide redireciona usuário para página de inscrição 
            com mensagem e erro.
            - caso valide:
                - verificar se esse usuário já possui autoria deste survey.
                - caso exista, resgate e atualize.
                - caso não exista, crie.
        """

        event_survey = lot.event_survey

        # verifica se o lote possui formulario(survey)
        if event_survey:
            # Se possui survey, ver se esse person que está respondendo já
            # possui autoria, ou seja já respondeu antes, caso de edição.
            # Se não possuir autoria, cria um novo autor, vincula

            survey_director = SurveyDirector(event=self.event,
                                             user=self.request.user)

            # Resgata e poupua um novo form para validação e persistencia.
            survey_form = survey_director.get_form(
                survey=event_survey.survey,
                data=self.request.POST.copy()
            )

            if not survey_form.is_valid() or not form.is_valid():

                all_surveys = survey_director.get_forms()

                surveys = []

                for new_form in all_surveys:

                    if new_form.survey.pk == survey_form.survey.pk:
                        surveys.append(survey_form)
                    else:
                        surveys.append(new_form)

                context['slug'] = kwargs.get('slug')
                context['form'] = form
                context['surveys'] = surveys
                return self.render_to_response(context)

            survey_form.save_answers()

        elif not form.is_valid():
            context['slug'] = kwargs.get('slug')
            context['form'] = form
            return self.render_to_response(context)

        person = form.save()

        # CONDIÇÃO 3
        new_account = user.last_login is None

        # CONDIÇÃO 4
        new_subscription = False

        try:
            subscription = Subscription.objects.get(
                person=person,
                event=self.event
            )
        except Subscription.DoesNotExist:
            subscription = Subscription(
                person=person,
                event=self.event,
                created_by=user.id
            )
            new_subscription = True

        # Insere ou edita lote
        subscription.lot = lot

        if lot.price is not None and lot.price > 0:
            # CONDIÇÃO 7
            if 'transaction_type' not in request.POST:
                messages.error(
                    request=self.request,
                    message='Por favor escolha um tipo de pagamento.'
                )
                return self.render_to_response(context)

            try:
                with transaction.atomic():

                    subscription.save()

                    transaction_data = PagarmeTransactionInstanceData(
                        subscription=subscription,
                        extra_data=request.POST.copy(),
                        event=self.event
                    )

                    create_pagarme_transaction(
                        transaction_data=transaction_data,
                        subscription=subscription
                    )

            except TransactionError as e:
                error_dict = {
                    'No transaction type': \
                        'Por favor escolher uma forma de pagamento.',
                    'Transaction type not allowed': \
                        'Forma de pagamento não permitida.',
                    'Organization has no bank account': \
                        'Organização não está podendo receber pagamentos no'
                        ' momento.',
                    'No organization': 'Evento não possui organizador.',
                }
                if e.message in error_dict:
                    e.message = error_dict[e.message]

                messages.error(self.request, message=e.message)
                return self.render_to_response(context)

        else:
            # CONDIÇÃO 8
            subscription.status = subscription.CONFIRMED_STATUS
            subscription.save()

            # CONDIÇÃO 5 e 7
            if new_account and new_subscription:
                notify_new_user_and_free_subscription(self.event, subscription)

            else:
                notify_new_free_subscription(self.event, subscription)

        messages.success(
            self.request,
            'Inscrição realizada com sucesso!'
        )

        if lot.price is not None and lot.price > 0:
            # CONDIÇÃO 7
            return redirect(
                'public:hotsite-subscription-status',
                slug=self.event.slug
            )

        # CONDIÇÃO 5
        return redirect('public:hotsite', slug=self.event.slug)


class SubscriptionLotFormView(SubscriptionFormMixin, generic.FormView):
    template_name = 'hotsite/subscription_lot_form.html'
    form_class = PersonForm

