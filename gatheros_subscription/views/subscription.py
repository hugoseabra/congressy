import base64
from datetime import datetime

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.transaction import atomic
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import generic
from wkhtmltopdf.views import PDFTemplateView

from core.forms.cleaners import clear_string
from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event, Person
from gatheros_event.views.mixins import (
    AccountMixin,
    PermissionDenied,
)
from gatheros_subscription.forms import (
    SubscriptionAttendanceForm,
    SubscriptionPersonForm,
    SubscriptionFilterForm,
    SubscriptionForm,
    SubscriptionCSVUploadForm,
)
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.helpers.report_payment import \
    PaymentReportCalculator
from gatheros_subscription.models import FormConfig, Lot, Subscription
from mailer import exception as mailer_exception, services as mailer
from payment import forms
from payment.helpers import payment_helpers
from payment.models import Transaction


class EventViewMixin(TemplateNameableMixin, AccountMixin):
    """ Mixin de view para vincular com informações de event. """
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()

        update_account(
            request=self.request,
            organization=self.event.organization,
            force=True
        )

        self.permission_denied_url = reverse('event:event-list')
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)

        event = self.get_event()
        context['event'] = event
        context['has_paid_lots'] = self.has_paid_lots()

        try:
            config = event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = event

        if self.has_paid_lots():
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        context['config'] = config

        return context

    def get_event(self):
        """ Resgata organização do contexto da view. """

        if self.event:
            return self.event

        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk')
        )
        return self.event

    def is_by_lots(self):
        return self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS

    def get_lots(self):
        return self.get_event().lots.filter(
            internal=False
        ).order_by('date_end', 'name')

    def get_num_lots(self):
        """ Recupera número de lotes a serem usados nas inscrições. """
        lot_qs = self.get_lots()
        return lot_qs.count() if lot_qs else 0

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():
            price = lot.price
            if price is None:
                continue

            if lot.price and lot.price > 0:
                return True

        return False

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization


class SubscriptionFormMixin(EventViewMixin, generic.FormView):
    template_name = 'subscription/form.html'
    form_class = SubscriptionPersonForm
    success_message = None
    subscription = None
    object = None
    allow_edit_lot = True
    error_url = None

    def get_error_url(self):
        return self.error_url

    def pre_dispatch(self, request):
        self.event = self.get_event()

        if self.event.allow_internal_subscription is False:
            self.permission_denied_url = reverse(
                'subscription:subscription-list', kwargs={
                    'event_pk': self.event.pk,
                }
            )
            raise PermissionDenied('Você não pode realizar esta ação.')

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            self.subscription = get_object_or_404(
                Subscription,
                pk=self.kwargs.get('pk')
            )
            self.object = self.subscription.person

            origin = self.subscription.origin
            self.allow_edit_lot = \
                origin == self.subscription.DEVICE_ORIGIN_MANAGE

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prefix'] = 'person'

        if self.object:
            kwargs['instance'] = self.object

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        lot_pk = self.request.GET.get('lot', 0)

        if not lot_pk and self.subscription:
            form.check_requirements(lot=self.subscription.lot)

        else:
            try:
                lot = self.event.lots.get(pk=int(lot_pk) if lot_pk else 0)
                form.check_requirements(lot=lot)

            except Lot.DoesNotExist:
                pass

        return form

    def get_subscription_form(self, person, lot_pk):
        data = {
            'person': person.pk,
            'lot': lot_pk,
            'origin': Subscription.DEVICE_ORIGIN_MANAGE,
            'created_by': self.request.user.pk,
            # 'completed': True,
        }

        kwargs = {'data': data}

        if self.subscription:
            kwargs['instance'] = self.subscription

        return SubscriptionForm(self.event, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'

        context['object'] = self.object
        context['allow_edit_lot'] = self.allow_edit_lot

        context['lots'] = [
            lot
            for lot in self.get_lots()
            if lot.status == lot.LOT_STATUS_RUNNING
               or (self.subscription and self.subscription.lot == lot)
        ]

        context['subscription'] = self.subscription

        lot_pk = self.request.GET.get('lot', 0)
        if not lot_pk and self.subscription:
            context['selected_lot'] = self.subscription.lot.pk

        else:
            context['selected_lot'] = int(lot_pk) if lot_pk else 0

        return context

    def post(self, request, *args, **kwargs):
        if self.allow_edit_lot and 'subscription-lot' not in request.POST:
            messages.warning(request, 'Você deve informar um lote.')
            return redirect(self.get_error_url())

        request.POST = request.POST.copy()

        to_be_pre_cleaned = [
            'person-cpf',
            'person-phone',
            'person-zip_code',
            'person-institution_cnpj'
        ]

        for field in to_be_pre_cleaned:
            if field in request.POST:
                request.POST[field] = clear_string(request.POST[field])

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if self.allow_edit_lot:
            lot_pk = self.request.POST.get('subscription-lot')

        elif self.subscription:
            lot_pk = self.subscription.lot.pk

        else:
            raise Exception('Edição de lote somente para nova inscrição.')

        with atomic():
            self.object = form.save()
            subscription_form = self.get_subscription_form(
                person=self.object,
                lot_pk=lot_pk,
            )
            if not subscription_form.is_valid():
                for error in subscription_form.errors:
                    messages.error(self.request, str(error))

                return redirect(self.get_error_url())

            self.subscription = subscription_form.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SubscriptionListView(EventViewMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/list.html'
    has_filter = False

    def get_queryset(self):
        query_set = super(SubscriptionListView, self).get_queryset()

        lots = self.request.GET.getlist('lots', [])
        if lots:
            query_set = query_set.filter(lot_id__in=lots)
            self.has_filter = True

        has_profile = self.request.GET.get('has_profile')
        if has_profile:
            query_set = query_set.filter(person__user__isnull=False)
            self.has_filter = True

        event = self.get_event()

        return query_set.filter(event=event, completed=True)

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionListView, self).get_context_data(**kwargs)

        cxt.update({
            'can_add_subscription': self.can_add_subscription(),
            'lots': self.get_lots(),
            'has_filter': self.has_filter,
            'has_paid_lots': self.has_paid_lots(),
            'has_inside_bar': True,
            'active': 'inscricoes',
        })
        return cxt

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )

    def can_add_subscription(self):
        event = self.get_event()
        if event.subscription_type == event.SUBSCRIPTION_SIMPLE:
            return True

        num_lots = self.get_num_lots()
        return num_lots > 0


class SubscriptionViewFormView(EventViewMixin, generic.DetailView):
    template_name = 'subscription/view.html'
    object = None
    queryset = Subscription.objects.get_queryset()
    financial = False
    last_transaction = None

    def get_form(self, **kwargs):
        return forms.ManualTransactionForm(
            subscription=self.get_object(),
            **kwargs
        )

    def get(self, request, *args, **kwargs):

        storage = messages.get_messages(request)

        messenger = []
        for message in list(storage):
            level_tag = message.level_tag
            if level_tag == 'danger':
                level_tag = 'error'

            messenger.append({
                'type': level_tag,
                'message': message.message,
            })

        storage._loaded_messages.clear()

        context = self.get_context_data(messenger=messenger)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        self.last_transaction = self._get_last_transaction()
        self.object = self.get_object()

        response = super().dispatch(request, *args, **kwargs)

        if self.financial is True:
            has_paid_products = self.object.subscription_products.filter(
                optional_price__gt=0
            ).count() > 0
            has_paid_services = self.object.subscription_services.filter(
                optional_price__gt=0
            ).count() > 0

            if not has_paid_products \
                    and not has_paid_products \
                    and self.object.free:
                messages.warning(
                    request,
                    'Este evento não possui relatório financeiro.'
                )

                return redirect(
                    'subscription:subscription-view',
                    event_pk=self.event.pk,
                    pk=self.object.pk,
                )

        return response

    def _get_last_transaction(self):
        """
        Recupera a transação mais recente.
        Primeiro verificando se há alguma paga. Se não, pega a mais recente.
        """
        queryset = self.get_object().transactions

        paid_transactions = queryset \
            .filter(status=Transaction.PAID) \
            .order_by('-date_created')

        if paid_transactions.count() > 0:
            return paid_transactions.first()

        return queryset.all().order_by('-date_created').first()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        calculator = PaymentReportCalculator(subscription=self.get_object())

        ctx['object'] = self.object
        ctx['lots'] = calculator.lots
        ctx['transactions'] = calculator.transactions
        ctx['full_prices'] = calculator.full_prices
        ctx['installments'] = calculator.installments
        ctx['has_manual'] = calculator.has_manual
        ctx['total_paid'] = calculator.total_paid
        ctx['dividend_amount'] = calculator.dividend_amount
        ctx['financial'] = self.financial
        ctx['last_transaction'] = self.last_transaction
        ctx['form'] = self.get_checkout_form()
        ctx['encryption_key'] = settings.PAGARME_ENCRYPTION_KEY
        ctx['services'] = self.get_services()
        ctx['products'] = self.get_products()
        ctx['new_boleto_allowed'] = payment_helpers.is_boleto_allowed(
            self.event
        )

        if self.request.GET.get('details'):
            ctx['show_details'] = True

        if 'manual_payment_form' not in ctx:
            ctx['manual_payment_form'] = self.get_form()

        return ctx

    def post(self, request, *args, **kwargs):
        url = reverse('subscription:subscription-payments', kwargs={
            'event_pk': self.event.pk,
            'pk': self.object.pk,
        })

        data = request.POST.copy()

        action = data.get('action')
        next_url = data.get('next_url')
        if action == 'notify_boleto':
            if next_url:
                url = next_url

            last_transaction = self._get_last_transaction()
            if not last_transaction.subscription.person.email:
                messages.error(request, 'Participante não possui e-mail.')
                return redirect(url)

            try:
                mailer.notify_open_boleto(
                    transaction=self._get_last_transaction()
                )
                messages.success(request, 'Boleto enviado com sucesso.')

            except mailer_exception.NotifcationError as e:
                messages.error(request, str(e))

            return redirect(url)

        if self.event.allow_internal_subscription is False:
            self.permission_denied_url = reverse(
                'subscription:subscription-list', kwargs={
                    'event_pk': self.event.pk,
                }
            )
            raise PermissionDenied('Você não pode realizar esta ação.')

        data['manual_author'] = '{} ({})'.format(
            request.user.get_full_name(),
            request.user.email,
        )
        kwargs = {'data': data}

        transaction_id = data.get('transaction_id')

        if transaction_id:
            instance = get_object_or_404(Transaction, pk=transaction_id)
            kwargs.update({'instance': instance})

        form = self.get_form(**kwargs)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(
                manual_payment_form=form,
                transaction_pk=transaction_id,
                modal='manual-payment',
            ))

        form.save()

        if transaction_id:
            messages.success(request, 'Recebimento editado com sucesso.')
        else:
            messages.success(request, 'Recebimento registrado com sucesso.')

        return redirect(url + '?details=1')

    def get_checkout_form(self):
        return forms.PagarMeCheckoutForm(
            initial={
                'subscription': self.object.pk,
                'next_url': reverse(
                    'subscription:subscription-payments',
                    kwargs={
                        'event_pk': self.event.pk,
                        'pk': self.object.pk,
                    }
                ),
            }
        )

    def get_products(self):
        return self.object.subscription_products.all()

    def get_services(self):
        return self.object.subscription_services.all()


class SubscriptionAddFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """
    success_message = 'Inscrição criada com sucesso.'

    def get_success_url(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

        if not self.subscription.free:
            return reverse('subscription:subscription-payments', kwargs={
                'event_pk': self.event.pk,
                'pk': self.subscription.pk,
            })

        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_error_url(self):
        return reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk
        })


class SubscriptionEditFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """
    success_message = 'Inscrição atualizada com sucesso.'
    allow_edit_lot = False

    def get_success_url(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_error_url(self):
        return reverse('subscription:subscription-edit', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })


class SubscriptionConfirmationView(EventViewMixin, generic.TemplateView):
    """ Inscrição de pessoa que já possui perfil. """
    subscription_user = None
    submitted_data = None
    template_name = 'subscription/subscription_confirmation.html'

    @classonlymethod
    def as_view(cls, user, submitted_data, **initkwargs):

        csrf = submitted_data.get('csrfmiddlewaretoken')
        if csrf:
            del submitted_data['csrfmiddlewaretoken']

        cleaned_submitted_data = {}
        for field_name, value in six.iteritems(dict(submitted_data)):
            if len(value) <= 1:
                cleaned_submitted_data[field_name] = value[0]
            else:
                cleaned_submitted_data[field_name] = value

        cls.subscription_user = user
        cls.submitted_data = cleaned_submitted_data

        return super(SubscriptionConfirmationView, cls).as_view(
            **initkwargs
        )

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionConfirmationView, self).get_context_data(
            **kwargs
        )
        cxt.update({
            'subscription_user': self.subscription_user,
            'submitted_data': self.submitted_data,
        })

        return cxt

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class SubscriptionCancelView(EventViewMixin, generic.DetailView):
    template_name = 'subscription/delete.html'
    model = Subscription
    success_message = 'Inscrição cancelada com sucesso.'
    cancel_message = 'Tem certeza que deseja cancelar?'
    model_protected_message = 'A entidade não pode ser cancelada.'
    place_organization = None
    object = None

    def get_object(self, queryset=None):
        """ Resgata objeto principal da view. """
        if not self.object:
            self.object = super(SubscriptionCancelView, self).get_object(
                queryset)

        return self.object

    def pre_dispatch(self, request):
        self.object = self.get_object()
        super(SubscriptionCancelView, self).pre_dispatch(request)

    def get_permission_denied_url(self):
        url = self.get_success_url()
        return url.format(**model_to_dict(self.object)) if self.object else url

    def get_context_data(self, **kwargs):
        context = super(SubscriptionCancelView, self).get_context_data(
            **kwargs)
        context['organization'] = self.organization
        context['go_back_path'] = self.get_success_url()
        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'

        # noinspection PyProtectedMember
        verbose_name = self.object._meta.verbose_name
        context['title'] = 'Cancelar {}'.format(verbose_name)

        data = model_to_dict(self.get_object())
        cancel_message = self.get_cancel_message()
        context['cancel_message'] = cancel_message.format(**data)
        return context

    def get_cancel_message(self):
        """
        Recupera mensagem de remoção a ser perguntada ao usuário antes da
        remoção.
        """
        return self.cancel_message

    def post(self, request, *args, **kwargs):
        try:

            pk = kwargs.get('pk')
            self.object = Subscription.objects.get(pk=pk)
            self.object.status = self.object.CANCELED_STATUS
            self.object.save()

            messages.success(request, self.success_message)

        except Exception as e:
            messages.error(request, str(e))

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })


class SubscriptionAttendanceDashboardView(EventViewMixin,
                                          generic.TemplateView):
    template_name = 'subscription/attendance-dashboard.html'
    search_by = 'name'

    def get_permission_denied_url(self):
        return reverse('event:event-list')

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt.update({
            'attendances': self.get_attendances(),
            'search_by': self.search_by,
            'has_inside_bar': True,
            'active': 'checkin-dashboard',
            'confirmed': self.get_number_confirmed(),
            'number_attendances': self.get_number_attendances(),
            'total_subscriptions': self.get_number_subscription(),
            'reports': self.get_report()
        })
        return cxt

    def get_attendances(self):
        try:
            list = Subscription.objects.filter(
                attended=True,
                completed=True,
                event=self.get_event(),
            ).order_by('-attended_on')
            return list[0:5]


        except Subscription.DoesNotExist:
            return []

    def get_number_attendances(self):
        try:
            return Subscription.objects.filter(
                attended=True,
                completed=True,
                event=self.get_event(),
            ).count()

        except Subscription.DoesNotExist:
            return 0

    def get_number_subscription(self):

        total = \
            Subscription.objects.filter(
                event=self.get_event(),
                completed=True,
            ).exclude(status=Subscription.CANCELED_STATUS).count()

        return total

    def get_number_confirmed(self):

        confirmed = \
            Subscription.objects.filter(
                status=Subscription.CONFIRMED_STATUS,
                completed=True,
                event=self.get_event()
            ).count()

        return confirmed

    def get_report(self):
        """ Resgata informações gerais do evento. """
        return self.get_event().get_report(only_attended=True)


class MySubscriptionsListView(AccountMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/my_subscriptions.html'
    ordering = ('event__name', 'event__date_start', 'event__date_end',)
    has_filter = False
    permission_denied_url = reverse_lazy('front:start')

    def get_queryset(self):
        person = self.request.user.person
        query_set = super(MySubscriptionsListView, self).get_queryset()

        # notcheckedin = self.request.GET.get('notcheckedin')
        # if notcheckedin:
        #     query_set = query_set.filter(attended=False)
        #     self.has_filter = True
        #
        # pastevents = self.request.GET.get('pastevents')
        # now = datetime.now()
        # if pastevents:
        #     query_set = query_set.filter(event__date_end__lt=now)
        #     self.has_filter = True
        #
        # else:
        #     query_set = query_set.filter(event__date_start__gt=now)

        return query_set.filter(
            person=person,
            completed=True,
            # event__published=True,
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, 'exists'):
            is_empty = not self.object_list.exists()
        else:
            is_empty = len(self.object_list) == 0

        if is_empty:
            return redirect(reverse('event:event-list'))

        return response

    def get_context_data(self, **kwargs):
        cxt = super(MySubscriptionsListView, self).get_context_data(**kwargs)
        cxt['has_filter'] = self.has_filter
        cxt['filter_events'] = self.get_events()
        cxt['needs_boleto_link'] = self.check_if_needs_boleto_link()
        # cxt['filter_categories'] = self.get_categories()
        return cxt

    def get_categories(self):
        """ Resgata categorias das inscrições existentes. """
        queryset = self.get_queryset()
        return queryset.values(
            'event__category__name',
            'event__category__id'
        ).distinct().order_by('event__category__name')

    def get_events(self):
        """ Resgata eventos dos inscrições o usuário possui inscrições. """
        queryset = self.get_queryset()
        return queryset.values(
            'event__name',
            'event__id',
        ).distinct().order_by('event__name')

    def can_access(self):
        try:
            self.request.user.person
        except Person.DoesNotExist:
            return False
        else:
            return True

    def check_if_needs_boleto_link(self):
        for subscription in self.object_list:

            if subscription.status == subscription.AWAITING_STATUS:

                for transaction in subscription.transactions.all():
                    if transaction.status == transaction.WAITING_PAYMENT and \
                                    transaction.type == 'boleto':
                        return True

        return False


class SubscriptionExportView(EventViewMixin, generic.View):
    http_method_names = ['post']
    template_name = 'subscription/export.html'
    form_class = SubscriptionFilterForm
    model = Subscription
    paginate_by = 5
    allow_empty = True
    event = None

    def get_event(self):
        if self.event:
            return self.event

        self.event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        return self.event

    def post(self, request, *args, **kwargs):
        # Chamando exportação
        output = export_event_data(self.get_event())

        # Criando resposta http com arquivo de download
        response = HttpResponse(
            output,
            content_type="application/vnd.ms-excel"
        )

        # Definindo nome do arquivo
        event = self.get_event()
        name = "%s_%s.xlsx" % (
            event.slug,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % name

        return response

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            Event.objects.get(pk=self.kwargs.get('event_pk'))
        )


class VoucherSubscriptionPDFView(AccountMixin, PDFTemplateView):
    template_name = 'pdf/voucher.html'
    subscription = None
    event = None
    person = None
    lot = None
    place = None
    show_content_in_browser = True
    permission_denied_url = reverse_lazy('front:start')

    cmd_options = {
        'margin-top': 5,
        'javascript-delay': 500,
    }

    def get_filename(self):
        return "{}-{}.pdf".format(self.event.slug, self.subscription.pk)

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)
        self.get_complementary_data()

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        context = super(VoucherSubscriptionPDFView, self).get_context_data(
            **kwargs)
        context['qrcode'] = self.generate_qr_code()
        context['logo'] = self.get_logo()
        context['event'] = self.event
        context['person'] = self.person
        context['lot'] = self.lot
        context['organization'] = self.event.organization
        context['subscription'] = self.subscription
        return context

    def get_logo(self):
        uri = staticfiles_storage.url('assets/img/logo_v3.png')
        url = settings.BASE_DIR + "/frontend" + uri
        with open(url, 'rb') as f:
            read_data = f.read()
            f.close()

        return base64.b64encode(read_data)

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )

        qr.add_data(self.subscription.uuid)

        qr.make(fit=True)

        img = qr.make_image()

        buffer = six.BytesIO()
        img.save(buffer)

        return base64.b64encode(buffer.getvalue())

    def get_complementary_data(self):
        self.event = self.subscription.event
        self.person = self.subscription.person
        self.lot = self.subscription.lot
        self.place = self.subscription.event.place

    def can_access(self):
        return self.subscription.confirmed is True


class SubscriptionAttendanceSearchView(EventViewMixin, generic.TemplateView):
    template_name = 'subscription/attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'checkin'
        return context


class SubscriptionAttendanceView(EventViewMixin, generic.FormView):
    form_class = SubscriptionAttendanceForm
    http_method_names = ['post']
    search_by = 'name'
    register_type = None
    object = None

    def get_object(self):
        if self.object:
            return self.object

        try:
            self.object = Subscription.objects.get(pk=self.kwargs.get('pk'))

        except Subscription.DoesNotExist:
            return None

        else:
            return self.object

    def get_success_url(self):
        url = reverse(
            'subscription:subscription-attendance-search',
            kwargs={'event_pk': self.kwargs.get('event_pk')}
        )
        if self.search_by is not None and self.search_by != 'name':
            url += '?search_by=' + str(self.search_by)

        return url

    def get_permission_denied_url(self):
        return self.get_success_url()

    def get_form_kwargs(self):
        kwargs = super(SubscriptionAttendanceView, self).get_form_kwargs()
        kwargs.update({'instance': self.get_object()})
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(SubscriptionAttendanceView, self).form_invalid(form)

    def form_valid(self, form):
        sub = self.get_object()

        try:
            if self.register_type is None:
                raise Exception('Nenhuma ação foi informada.')

            register_name = 'Credenciamento' \
                if self.register_type == 'register' \
                else 'Cancelamento de credenciamento'

        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

        else:
            messages.success(
                self.request,
                '{} de `{}` registrado com sucesso.'.format(
                    register_name,
                    sub.person.name
                )
            )
            form.attended(self.register_type == 'register')
            return super(SubscriptionAttendanceView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.search_by = request.POST.get('search_by')
        self.register_type = request.POST.get('action')

        return super(SubscriptionAttendanceView, self).post(
            request,
            *args,
            **kwargs
        )

    def can_access(self):
        event = self.get_event()
        sub = self.get_object()
        return sub.event.pk == event.pk


class SubscriptionAttendanceListView(EventViewMixin, generic.TemplateView):
    template_name = 'subscription/attendance-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendances'] = self.get_attendances()
        context['has_inside_bar'] = True
        context['active'] = 'checkin-list'
        return context

    def get_attendances(self):
        return Subscription.objects.filter(
            attended=True,
            completed=True,
            event=self.get_event(),
        ).exclude(status=Subscription.CANCELED_STATUS).order_by('-attended_on')


class SubscriptionCSVImportView(EventViewMixin, generic.FormView):

    form_class = SubscriptionCSVUploadForm
    template_name = "subscription/csv_import.html"



