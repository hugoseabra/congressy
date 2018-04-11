from django import forms
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import generic

from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Person
from gatheros_subscription.models import FormConfig, Lot, \
    Subscription
from hotsite.forms import LotsForm, SubscriptionPersonForm
from hotsite.views.mixins import SubscriptionFormMixin, EventMixin
from hotsite.views.subscription_form_bootstrappers import LotBootstrapper
from hotsite.views.subscription_form_steps import StepOne, StepTwo, \
    StepThree, StepFour
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.tasks import create_pagarme_transaction
from survey.directors import SurveyDirector


#
# # Survey (Se existir)
# def step_3(request, event, person, lot):
#     if not lot:
#         return step_1(request, event=event)
#
#     if not isinstance(lot, Lot) and isinstance(int(lot), Lot):
#
#         if isinstance(int(lot), int):
#             try:
#                 lot = Lot.objects.get(pk=int(lot), event=self.event)
#             except Lot.DoesNotExist:
#                 pass
#
#     if not person:
#         return step_2(request, event=event)


# # Dados pessoais
# def step_2(request, event, lot=None, form=None):
#     if not lot and not form:
#         step_1 = StepOne(
#             request=request,
#             event=event,
#             context={
#                 'event': event,
#                 'remove_preloader': True
#             })
#
#         return step_1.render()
#
#     if not lot:
#
#         lot = form.event_lot
#
#         if not isinstance(lot, Lot):
#             return step_1(request, event=event)
#
#     if not form:
#         form = SubscriptionPersonForm(lot=lot,
#                                       initial={
#                                           'next_step': 2,
#                                           'lot': lot.pk},
#                                       event=event
#                                       )
#
#     context = {'form': form, 'event': lot.event}
#
#     try:
#         config = lot.event.formconfig
#     except AttributeError:
#         config = FormConfig()
#
#     if lot.price > 0:
#         config.email = True
#         config.phone = True
#         config.city = True
#
#         config.cpf = config.CPF_REQUIRED
#         config.birth_date = config.BIRTH_DATE_REQUIRED
#         config.address = config.ADDRESS_SHOW
#
#     context['config'] = config
#     context['remove_preloader'] = True
#     context['has_lots'] = lot.event.lots.count() > 1
#
#     response = render(request, 'hotsite/person_form.html', context)
#
#     return response


#
# # Survey (Se existir)
# def step_3(request, event, person, lot):
#     if not lot:
#         return step_1(request, event=event)
#
#     if not isinstance(lot, Lot) and isinstance(int(lot), Lot):
#
#         if isinstance(int(lot), int):
#             try:
#                 lot = Lot.objects.get(pk=int(lot), event=self.event)
#             except Lot.DoesNotExist:
#                 pass
#
#     if not person:
#         return step_2(request, event=event)
#
#
# # Pagamentos (Se existir)
# def step_4(request, person, lot, survey=None):
#     pass
#
#
# # Salva inscrição e redireciona para pagina de status.
# def step_5(request):
#     pass

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


class SubscriptionFormIndexView(EventMixin, generic.View):
    """
        View responsavel por decidir onde se inicia o process de inscrição
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()
        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get(self, request, *args, **kwargs):

        """
            Se for evento com inscrição por lotes, ir para o step 1,
            caso contrario pode pular direto para o step 2.
        """
        if self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS:

            step_1 = StepOne(
                request=request,
                event=self.event,
                context={
                    'event': self.event,
                    'remove_preloader': True
                })

            return step_1.render()

        elif self.event.subscription_type == Event.SUBSCRIPTION_SIMPLE:

            lot = self.event.lots.first()

            step_2 = StepTwo(request=request, event=self.event,
                             dependency_artifacts={'lot': lot}, )

            return step_2.render()

    def post(self, request, *args, **kwargs):

        incoming_step = request.POST.get('next_step', 0)

        if not incoming_step:
            incoming_step = 0

        next_step = int(incoming_step)

        if next_step == 0:

            step_1 = StepOne(
                request=request,
                event=self.event,
                context={
                    'event': self.event,
                    'remove_preloader': True
                })

            return step_1.render()

        elif next_step == 1:

            form = LotsForm(event=self.event, data=request.POST)

            if form.is_valid():
                lot = form.cleaned_data['lots']

                form = None

                try:

                    person = Person.objects.get(user=self.request.user)
                    form = SubscriptionPersonForm(instance=person,
                                                  event=self.event,
                                                  lot=lot,
                                                  initial={
                                                      'next_step': 2,
                                                      'lot': lot.pk}
                                                  )
                except Person.DoesNotExist:
                    pass

                step_2 = StepTwo(request=request, event=self.event,
                                 form=form,
                                 dependency_artifacts={'lot': lot})

                return step_2.render()

            # Form did not validate, re-render step #1 and retrieve a lot
            # correctly.
            step_1 = StepOne(
                request=request,
                event=self.event,
                context={
                    'event': self.event,
                    'remove_preloader': True
                },
                form=form,
            )

            return step_1.render()

        elif next_step == 2:

            lot_pk = request.POST.get('lot', None)
            lot_bootstrapper = LotBootstrapper(lot_pk=lot_pk, event=self.event)
            lot = lot_bootstrapper.retrieve_artifact()

            if not lot:
                step_1 = StepOne(
                    request=request,
                    event=self.event,
                    context={
                        'event': self.event,
                        'remove_preloader': True
                    })
                return step_1.render()

            # Pre-form cleaning
            # This is a hack. Please don't do this.
            # Ref: https://stackoverflow.com/questions/12611345/django-why-is-the-request-post-object-immutable
            mutable = self.request.POST._mutable
            self.request.POST._mutable = True

            self.clear_string('cpf')
            self.clear_string('zip_code')
            self.clear_string('phone')
            self.clear_string('institution_cnpj')

            self.request.POST._mutable = mutable

            try:
                person = Person.objects.get(user=self.request.user)
                form = SubscriptionPersonForm(instance=person,
                                              event=self.event,
                                              data=request.POST,
                                              lot=lot)
            except Person.DoesNotExist:
                form = SubscriptionPersonForm(event=self.event,
                                              lot=lot,
                                              data=request.POST)

            if form.is_valid():

                person = form.save()

                if not person.user:
                    person.user = self.request.user
                    person.save()

                try:
                    subscription = Subscription.objects.get(
                        person=person,
                        event=self.event
                    )
                except Subscription.DoesNotExist:
                    subscription = Subscription(
                        person=person,
                        event=self.event,
                        created_by=self.request.user.id
                    )

                subscription.lot = lot
                subscription.save()

                """
                    Se o lote possuir surveys, ir para step 3.
                    
                    Se o lote não possuir surveys, e possuir pagamento ir para 
                    step 4
                    
                    Se o lote não possuir surveys, e não possuir pagamento ir 
                    para step 5.
                    
                """
                event_survey = lot.event_survey
                lot_price = lot.price

                if event_survey:
                    survey_director = SurveyDirector(event=self.event,
                                                     user=self.request.user)

                    survey_form = survey_director.get_form(
                        survey=event_survey.survey)

                    survey_form.fields['next_step'] = forms.IntegerField(
                        initial=3,
                        widget=forms.HiddenInput()
                    )
                    survey_form.fields['subscription'] = forms.CharField(
                        initial=str(subscription.pk),
                        max_length=60,
                        widget=forms.HiddenInput()
                    )

                    # Se o lote possuir surveys, ir para step 3.
                    step_3 = StepThree(request=request, event=self.event,
                                       form=survey_form)

                    return step_3.render()

                if lot_price > 0:
                    # Se o lote não possuir surveys, e possuir pagamentos ir
                    # para step 4.
                    step_4 = StepFour(request=request, event=self.event,
                                      dependency_artifacts={'subscription':
                                                                subscription})
                    return step_4.render()

                # # verifica se o lote possui formulario(survey)
                # if event_survey:
                #     # Se possui survey, ver se esse person que está respondendo já
                #     # possui autoria, ou seja já respondeu antes, caso de edição.
                #     # Se não possuir autoria, cria um novo autor, vincula
                #

                #
                #     if not survey_form.is_valid() or not form.is_valid():
                #
                #         all_surveys = survey_director.get_forms()
                #
                #         surveys = []
                #
                #         for new_form in all_surveys:
                #
                #             if new_form.survey.pk == survey_form.survey.pk:
                #                 surveys.append(survey_form)
                #             else:
                #                 surveys.append(new_form)
                #
                #         context['slug'] = kwargs.get('slug')
                #         context['form'] = form
                #         context['surveys'] = surveys
                #         return self.render_to_response(context)
                #
                #     survey_form.save_answers()

                # if lot.event_survey:
                #     return step_3(request, person, lot)
                # else:
                #     return step_4(request, person, lot, )
                #

            # Form is not valid, re-render step 2, person form.
            step_2 = StepTwo(request=request, event=self.event,
                             form=form, dependency_artifacts={'lot': lot})
            return step_2.render()

        elif next_step == 3:
            print('sdasdas')


        #
        # elif next_step == 3:
        #     raise Exception('not there yet bucko')
        # elif next_step == 4:
        #     raise Exception('not there yet bucko')
        else:
            return HttpResponseBadRequest()

    def clear_string(self, field_name):

        if field_name not in self.request.POST:
            return

        value = self.request.POST.get(field_name)

        if not value:
            return ''

        value = value \
            .replace('.', '') \
            .replace('-', '') \
            .replace('/', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(' ', '')

        self.request.POST[field_name] = value
