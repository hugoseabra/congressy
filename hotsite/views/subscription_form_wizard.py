from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.transaction import atomic
from django.forms import ValidationError
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView

from core.helpers import sentry_log
from core.util.string import clear_string
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.directors import SubscriptionSurveyDirector
from gatheros_subscription.models import Subscription
from hotsite import forms
from hotsite.views.mixins import SelectTicketMixin
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers.payment_helpers import (
    get_opened_boleto_transactions,
    is_boleto_allowed,
)
from payment.models import Transaction
# from survey.directors import SurveyDirector - TODO: Depreciate this director
from survey.models import Question
from ticket.models import Ticket

FORMS = [
    ("private_ticket", forms.PrivateTicketForm),
    ("ticket", forms.TicketForm),
    ("service", forms.ServiceForm),
    ("product", forms.ProductForm),
    ("person", forms.SubscriptionPersonForm),
    ("survey", forms.SurveyForm),
    ("payment", forms.PaymentForm)
]

TEMPLATES = {
    "private_ticket": "hotsite/private_ticket_form.html",
    "ticket": "hotsite/ticket_form.html",
    "service": "hotsite/service_form.html",
    "product": "hotsite/product_form.html",
    "person": "hotsite/person_form.html",
    "survey": "hotsite/survey_form.html",
    "payment": "hotsite/payment_form.html"
}


class InvalidStateStepError(Exception):
    """ Exceção acontece quando um step de formulário não possui
     um estado esperado. """
    pass


def get_selected_ticket(wizard):
    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('private_ticket')
    if not cleaned_data:
        cleaned_data = wizard.get_cleaned_data_for_step('ticket')

    # Return true if lot has price and price > 0
    if not cleaned_data:
        return None

    ticket = cleaned_data.get('ticket')
    if not ticket:
        return None

    if not isinstance(ticket, Ticket):
        try:
            ticket = Ticket.objects.get(pk=ticket)

            return ticket

        except Ticket.DoesNotExist:
            return None


def is_paid_ticket(wizard):
    """Return true if user opts for  a paid lot"""
    ticket = get_selected_ticket(wizard)
    return ticket.price > 0 if ticket else False


def has_pending_payment(wizard):
    subscription = wizard.subscription

    ##########################################################################
    # Verifica se já existe pagamentos aguardando serem processados.
    ##########################################################################
    for transaction in subscription.transactions.all():
        is_cc = transaction.type == Transaction.CREDIT_CARD
        is_boleto = transaction.type == Transaction.BOLETO
        boleto_expiration_date = transaction.boleto_expiration_date
        today = datetime.date(datetime.now())
        if transaction.status == Transaction.WAITING_PAYMENT:

            if is_boleto:
                if boleto_expiration_date \
                        and boleto_expiration_date < today:
                    return False
                else:
                    return True

            if is_cc:
                return True

        # NO caso de cartão de crédito, pode haver um delay no processamento
        if transaction.status == Transaction.PROCESSING and is_cc:
            return True

    return False


def can_process_payment(wizard):
    """ Verifica se pagamento pode ser processado no wizard. """
    if wizard.storage.current_step == "payment":
        return True

    subscription = wizard.subscription

    ##########################################################################
    # Verifica se existe inscrições e existe necessidade de processamento
    # de pagamento.
    ##########################################################################
    paid_ticket = is_paid_ticket(wizard)

    if paid_ticket is False:
        # Se é de um lote gratuito:
        ev_has_paid_products = has_paid_products(wizard)
        ev_has_paid_services = has_paid_services(wizard)

        if ev_has_paid_services is False and ev_has_paid_products is False:
            # Para eventos gratuitos que não possuem atividades extras ou
            # opcionais pagos, não processar pagamento.
            return False

        # Verificando se inscrição possui vínculo com alguma das atividades
        # extras e/ou opcionais.
        num_paid_products = subscription.subscription_products.filter(
            optional__price__gt=0
        ).count()
        num_paid_services = subscription.subscription_services.filter(
            optional__price__gt=0
        ).count()

        if num_paid_products == 0 and num_paid_services == 0:
            # Se a inscrição não possui vinculo com atividades  extras e
            # opcionais pagos.
            return False

    # Se o lote selecionado é pago, independente das atividades extras e/ou
    # opcionais, o pagamento poderá ser processado.

    if has_pending_payment(wizard):
        # Porém, se inscrição já possui pagamento pendente.
        return False

    # Tudo certo, vamos processar o pagamento.
    return True


def has_survey(wizard):
    """ Return true if user opts for a lot with survey"""

    ticket = get_selected_ticket(wizard)
    if not ticket:
        return False

    if ticket.event.feature_configuration.feature_survey is False:
        return False

    return ticket.event_survey_id and \
           ticket.event_survey.survey.questions.count()


def is_private_event(wizard):
    return wizard.current_event.is_private_event()


def is_not_private_event(wizard):
    return not wizard.current_event.is_private_event()


def has_products(wizard):
    ticket = get_selected_ticket(wizard)
    if not ticket:
        return False

    if ticket.event.feature_configuration.feature_products is False:
        return False

    try:
        return ticket.addon_products.filter(
            published=True,
            date_end_sub__gte=datetime.now(),
        ).count() > 0

    except AttributeError:
        return False


def has_services(wizard):
    ticket = get_selected_ticket(wizard)
    if not ticket:
        return False

    if ticket.event.feature_configuration.feature_services is False:
        return False

    try:
        return ticket.addon_services.filter(
            published=True,
            date_end_sub__gte=datetime.now(),
        ).count() > 0

    except AttributeError:
        return False


def has_paid_products(wizard):
    ticket = get_selected_ticket(wizard)
    if not ticket:
        return False

    if ticket.event.feature_configuration.feature_products is False:
        return False

    try:
        return ticket.addon_services.filter(
            published=True,
            liquid_price__gt=0,
            date_end_sub__gte=datetime.now(),
        ).count() > 0

    except AttributeError:
        return False


def has_paid_services(wizard):
    ticket = get_selected_ticket(wizard)
    if not ticket:
        return False

    if ticket.event.feature_configuration.feature_services is False:
        return False

    return ticket.addon_services.filter(
        published=True,
        liquid_price__gt=0,
        date_end_sub__gte=datetime.now(),
    ).count() > 0


class SubscriptionWizardView(SessionWizardView, SelectTicketMixin):
    # file_storage = FileSystemStorage(
    #     location=os.path.join(settings.MEDIA_ROOT, 'survey', 'pdfs')
    # )
    condition_dict = {
        'private_ticket': is_private_event,
        'ticket': is_not_private_event,
        'payment': can_process_payment,
        'survey': has_survey,
        'service': has_services,
        'product': has_products,
    }

    def __init__(self, **initkwargs):
        self.event = None
        self.subscription = None
        self.top_bar = False
        self.loaded_forms = {}
        super().__init__(**initkwargs)

    def pre_dispatch(self):
        super().pre_dispatch()

        self.event = self.current_event.event
        self.subscription = self.current_subscription.subscription

        if 'conversion_unique_id' not in self.request.session:
            # Ponto de controle para saber que participante passou pelo
            # wizard e leva informação para o /subscription/done/
            self.request.session['conversion_unique_id'] = \
                str(self.subscription.pk)

    def dispatch(self, request, *args, **kwargs):
        path = request.path
        self.top_bar = '/subscription/' in path

        self.pre_dispatch()

        user = self.request.user
        if not isinstance(user, User):
            messages.warning(
                request,
                "Você não está logado, por favor faça seu login. "
            )
            return redirect('public:hotsite', slug=self.event.slug)

        if not self.current_event.subscription_enabled():
            messages.warning(
                request,
                "Evento não está permitindo inscrições."
            )
            return redirect('public:hotsite', slug=self.event.slug)

        # try:
        if self.current_subscription.has_payments():
            messages.warning(
                request,
                "Você já possui uma inscrição paga neste evento."
            )

        if self.current_event.is_private_event():

            code = self.get_exhibition_code()

            if self.is_valid_exhibition_code(code) is False:
                messages.error(
                    request,
                    "Você deve informar um código válido para se inscrever"
                    " neste evento."
                )
                self.clear_session_exhibition_code()
                return redirect('public:hotsite', slug=self.event.slug)

        return super().dispatch(request, *args, **kwargs)

        # except InvalidStateStepError as e:
        #
        #     sentry_log(str(e), type='error', notify_admins=True)
        #
        #     messages.warning(
        #         request,
        #         "Por favor, informe os dados do início para validarmos"
        #         " as informações de sua inscrição."
        #     )
        #
        #     return redirect('public:hotsite-subscription',
        #                     slug=self.event.slug)

    def post(self, *args, **kwargs):
        """
        This method handles POST requests.

        The wizard will render either the current step (if form validation
        wasn't successful), the next step (if the current step was stored
        successful) or the done view (if no more steps are available)
        """
        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).

        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)

        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                _('ManagementForm data is missing or has been tampered.'),
                code='missing_management_form',
            )

        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step

        # @TODO: Fix this ugly hack for pre-form cleaning
        # Copy is needed, QueryDict is immutable
        post_data = self.request.POST.copy()
        post_data = self.clear_string('person-institution_cnpj',
                                      data=post_data)
        post_data = self.clear_string('person-cpf', data=post_data)
        post_data = self.clear_string('person-zip_code', data=post_data)
        post_data = self.clear_string('person-phone', data=post_data)

        # get the form for the current step
        # @TODO: Fix this ugly hack for pre-form cleaning
        # This should be receiving self.request.POST no post_data
        form = self.get_form(data=post_data, files=self.request.FILES)

        # and try to validate
        while form.is_valid():
            # if the form is valid, store the cleaned data and files.
            try:
                self.storage.set_step_data(self.steps.current,
                                           self.process_step(form))
                # self.storage.set_step_files(self.steps.current,
                #                             self.process_step_files(form))
            except ValidationError as e:

                if hasattr(e, 'message'):
                    form.add_error('__all__', e.message)
                elif hasattr(e, 'error_dict'):
                    for field, err in e:
                        form.add_error(field, err)
                elif hasattr(e, 'error_list'):
                    for err in e:
                        form.add_error('__all__', err)
                else:
                    raise Exception('Unknown ValidationError message.')
                break

            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form, **kwargs)

        return self.render(form)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        if step in self.loaded_forms and data is None:
            form = self.loaded_forms[step]
            if form.data is None:
                return self.loaded_forms[step]

        # Submissão a partir da seleção de ingresso
        if step in ['ticket', 'private_ticket'] and data:
            if data.get('coupon'):
                self.request.session['exhibition_code'] = data.get('coupon')

        form = super().get_form(step, data, files)
        self.loaded_forms[step] = form
        return form

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step in ['private_ticket', 'ticket']:
            kwargs.update({
                'event': self.event,
                'code': self.get_exhibition_code(),
                'excluded_ticket_pk': None,
            })

        if step == 'person':
            kwargs.update({
                'user': self.request.user,
                'event': self.event,
            })

        if step == 'survey':
            ticket = self.get_ticket()

            kwargs.update({
                'subscription': self.current_subscription.subscription,
                'ticket': self.get_ticket(),
                'event_survey':
                    ticket.event_survey
                    if ticket and ticket.event_survey_id
                    else None,
            })

        if step == 'payment':
            kwargs.update({
                'selected_ticket': self.get_ticket(),
                'subscription': self.current_subscription.subscription,
            })

        return kwargs

    def process_step(self, form):

        if not form.is_valid():
            raise ValidationError(form.errors)

        form_data = self.get_form_step_data(form)
        form_files = self.get_form_step_files(form)

        # Creating a subscription.
        if isinstance(form, forms.TicketForm) or \
                isinstance(form, forms.PrivateTicketForm):

            ticket_pk = None
            if isinstance(form, forms.PrivateTicketForm):
                ticket_pk = form_data.get('private_ticket-ticket')

            elif isinstance(form, forms.TicketForm):
                ticket_pk = form_data.get('ticket-ticket')

            try:
                ticket = Ticket.objects.get(pk=ticket_pk)
            except Ticket.DoesNotExist:
                raise InvalidStateStepError(
                    'Não foi possivel pegar uma referencia de ingresso.'
                )

            # persistir lote selecionado para ser usado posteriormente.
            self.request.session['ticket_pk'] = ticket_pk
            self.subscription = self.current_subscription.subscription
            self.subscription.ticket_lot = ticket.current_lot

            # Se nova inscrição, não há problemas em setar o lote por aqui.
            # Se inscrição preexistente, o lote não pode ser setado porque
            # seria uma edição precoce do processo. O lote deve ser firmado
            # no 'done'.
            if self.subscription.brand_new is True:
                self.subscription.save()

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            if not form.is_valid():
                raise ValidationError(form.errors)

            self.person = form.save()

        # Persisting survey
        if isinstance(form, forms.SurveyForm):

            ticket = self.get_ticket()
            survey = ticket.event_survey.survey \
                if ticket.event_survey_id \
                else None

            if survey is None:
                raise Exception(
                    'Uma tentaiva de processar formulário de perguntas foi'
                    ' realizada, porém não há formulários disponíveis..'
                )

            # Tratamento especial para extrair as respostas do form_data,
            # causado pelo uso do FormWizard que adiciona prefixos nas
            # respostas
            questions_that_need_parsing = Question.objects.filter(
                type=Question.FIELD_CHECKBOX_GROUP,
                survey_id=survey.pk,
            ).values_list("name")

            needs_parsing = [x[0] for x in questions_that_need_parsing]

            survey_data = dict()
            for question, answer in form_data.items():
                if question == 'csrfmiddlewaretoken':
                    survey_data.update({question: answer})

                if 'survey-' in question:
                    raw_question_name = question
                    question_name = question.replace('survey-', '')

                    if question_name in needs_parsing:
                        answer_list = form_data.getlist(raw_question_name)
                        if not len(answer_list):
                            answer_list = list()
                            answer_list.append(answer)

                        answer = answer_list

                    survey_data[question_name] = answer

            # TODO: MAYBE WE CAN CHANGE QUERYDICT INSTANCE TO A SIMPLE DICT ???
            survey_files = QueryDict('', mutable=True)
            for form_question, uploaded_file in form_files.items():
                if form_question == 'csrfmiddlewaretoken':
                    survey_files.update({form_question: uploaded_file})

                if 'survey-' in form_question:
                    survey_files.update({
                        form_question.replace('survey-', ''): uploaded_file
                    })

            survey_director = SubscriptionSurveyDirector(self.subscription)

            survey_form = survey_director.get_active_form(
                survey=survey,
                data=survey_data,
                files=survey_files,
                update=self.request.method in ['POST', 'PUT']
            )

            if not survey_form.is_valid():
                raise ValidationError(survey_form.errors)

            survey_form.save()

            if self.subscription.brand_new is True:
                self.subscription.author_id = survey_form.author.pk
                self.subscription.save()

        # Persisting payments:
        if isinstance(form, forms.PaymentForm):
            if not form.is_valid():
                raise ValidationError(form.errors)

            try:
                form.save()

            except TransactionError as e:
                raise ValidationError(str(e))

        return form_data

    def get_next_step(self, step=None):
        """
        Returns the next step after the given `step`. If no more steps are
        available, None will be returned. If the `step` argument is None, the
        current step will be determined automatically.
        """
        if step is None:
            step = self.steps.current
        form_list = self.get_form_list()
        keys = list(form_list.keys())

        # This is a hack, to return to the first step, when we get a ValueError
        # See: https://intra.congressy.com/congressy/congressy/issues/2453/
        try:
            key = keys.index(step) + 1
        except ValueError:
            return keys[0]

        if len(keys) > key:
            return keys[key]
        return None

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True

        context['num_tickets'] = \
            len(self.current_event.get_available_tickets())
        context['exhibition_code'] = self.get_exhibition_code()
        context['subscription'] = self.subscription
        context['is_last'] = self.steps.current == self.steps.last
        context['has_top_bar'] = self.top_bar
        has_open_boleto = False

        person = self.subscription.person
        context['person'] = person

        opened_boletos = self.get_open_boleto()
        context['has_open_boleto'] = has_open_boleto

        if self.storage.current_step == 'ticket':
            has_open_boleto = \
                opened_boletos.count() > 0 if opened_boletos else False

        elif self.storage.current_step == 'private_ticket':
            code = self.request.session.get('exhibition_code')
            if self.is_valid_exhibition_code(code):
                tickets = Ticket.objects.filter(
                    private=True,
                    exhibition_code=code.upper(),
                )
                if tickets:
                    context['selected_ticket'] = tickets.first()

        else:
            context['selected_ticket'] = self.get_ticket()

        if self.storage.current_step == 'ticket':
            context['has_coupon'] = self.current_event.has_coupon()

        if self.storage.current_step == 'person':
            config = self.current_event.form_config

            if is_paid_event(self.current_event.event):
                config.email = True
                config.phone = True
                config.city = True

                config.cpf = config.CPF_REQUIRED
                config.birth_date = config.BIRTH_DATE_REQUIRED
                config.address = config.ADDRESS_SHOW

            context['config'] = config

        if self.storage.current_step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

            allowed_types = [Transaction.CREDIT_CARD]
            is_brazilian = person.country == 'BR'

            if is_boleto_allowed(self.event) \
                    and has_open_boleto is False \
                    and is_brazilian is True:
                allowed_types.append(Transaction.BOLETO)

            context['allowed_transaction_types'] = ','.join(allowed_types)

            subscription = self.subscription
            context['subscription'] = subscription

            total = \
                subscription.ticket_lot.get_subscriber_price() or Decimal(0.00)

            products = subscription.subscription_products.all()
            context['products'] = products

            services = subscription.subscription_services.all()
            context['services'] = services

            for product in products:
                total += product.optional.price

            for service in services:
                total += service.optional.price

            context['total'] = total

        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):

        if 'has_private_subscription' in self.request.session:
            del self.request.session['has_private_subscription']

        subscription = self.subscription

        with atomic():
            try:
                subscription.completed = True
                subscription.save()
                transactions_qs = self.subscription.transactions

                has_paid_optionals = \
                    self.current_subscription.has_paid_optionals()
                is_free = has_paid_optionals is False and subscription.free

                new_account = self.request.user.last_login is None

                if is_free:
                    subscription.status = Subscription.CONFIRMED_STATUS
                    subscription.save()

                    if self.current_subscription.has_payments() is True:

                        msg_trans = 'Você possui pagamento de outro ingresso.'
                        messages.warning(self.request, msg_trans)

                    elif self.current_subscription.has_transactions() is True:
                        msg_trans = 'Por favor, ignore os boletos que ainda' \
                                    ' não estejam vencidos.'
                        messages.warning(self.request, msg_trans)

                    notified = self.subscription.brand_new \
                               or self.subscription.has_changed('ticket_lot')

                    if notified is False \
                            or self.subscription.notified is False:

                        if new_account is True:
                            notify_new_user_and_free_subscription(
                                self.event,
                                subscription
                            )

                        else:
                            notify_new_free_subscription(
                                self.event,
                                subscription
                            )

                        msg = 'Inscrição realizada com sucesso!' \
                              ' Nós lhe enviamos um e-mail de confirmação de' \
                              ' sua inscrição juntamente com seu voucher.' \
                              ' Fique atento ao seu email, e, caso não' \
                              ' chegue na caixa de entrada, verifique no' \
                              ' Lixo Eletrônico.'

                        subscription.notified = True
                        subscription.save()

                    else:
                        msg = 'Inscrição salva com sucesso!'

                else:

                    has_transactions = transactions_qs.exclude(
                        subscription__ticket_lot_id=subscription.ticket_lot_id
                    ).count() > 0

                    if has_transactions is True:
                        paid_transaction = transactions_qs.filter(
                            status=Transaction.PAID
                        ).exclude(
                            subscription__ticket_lot_id=subscription.ticket_lot_id
                        ).count() > 0

                        if paid_transaction is True:
                            msg_trans = 'Você já possui pagamento de' \
                                        ' de outro lote.'
                            messages.warning(self.request, msg_trans)

                        msg_trans = 'Por favor, ignore os boletos que ainda' \
                                    ' não estejam vencidos.'

                        messages.warning(self.request, msg_trans)

                    notified = self.subscription.brand_new \
                               or self.subscription.has_changed('ticket_lot')

                    if notified is False \
                            or self.subscription.notified is False:
                        msg = 'Inscrição realizada com sucesso! Nós lhe' \
                              ' enviamos um e-mail de confirmação de sua' \
                              ' inscrição. Após a confirmação de seu' \
                              ' pagamento, você receberá outro email com' \
                              ' seu voucher. Fique atento ao seu email, e,' \
                              ' caso não chegue na caixa de entrada,' \
                              ' verifique no Lixo Eletrônico.'
                    else:
                        msg = 'Inscrição salva com sucesso!'

                success_url = reverse_lazy(
                    'public:hotsite-subscription-done',
                    kwargs={'slug': self.event.slug, }
                )

                self.clear_session()

                messages.success(self.request, msg)
                return redirect(success_url)

            except Exception as e:
                self.clear_session()

                raise InvalidStateStepError('Algum erro ocorreu: {}'.format(e))

    def get_ticket(self):
        selected_ticket = get_selected_ticket(self)

        if not selected_ticket:
            raise InvalidStateStepError('Nenhum ingresso selecionado.')

        return selected_ticket

    def get_exhibition_code(self):
        return self.request.session.get('exhibition_code')

    def get_exhibition_code_ticket(self, code):
        if code:
            for ticket in self.current_event.get_available_tickets():
                ticket_code = ticket.exhibition_code
                if ticket_code and ticket_code.upper() == code.upper():
                    return ticket

        return None

    def is_valid_exhibition_code(self, code):
        """
        Verifica se código de exibição informado é válido para o evento.
        """
        return self.get_exhibition_code_ticket(code) is not None

    def clear_session_exhibition_code(self):
        if 'exhibition_code' in self.request.session:
            del self.request.session['exhibition_code']

    def clear_session(self):
        def remove_session_key(key):
            if key in self.request.session:
                del self.request.session[key]

        self.clear_session_exhibition_code()
        remove_session_key('has_private_subscription')
        remove_session_key('ticket_pk')

    def get_open_boleto(self):
        return get_opened_boleto_transactions(self.subscription)

    def clear_string(self, field_name, data):
        if data and field_name in data:
            value = data.get(field_name)
            if value:
                data[field_name] = clear_string(value)
        return data
