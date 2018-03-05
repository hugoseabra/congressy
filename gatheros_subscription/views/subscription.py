import base64
from datetime import datetime

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Model
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import generic
from wkhtmltopdf.views import PDFTemplateView

from gatheros_event.forms import PersonForm
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event, Person
from gatheros_event.views.mixins import (
    AccountMixin,
)
from gatheros_subscription.forms import (
    SubscriptionForm,
    SubscriptionFilterForm
)
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.models import Subscription, FormConfig


class EventViewMixin(AccountMixin, generic.View):
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
        context = super(EventViewMixin, self).get_context_data(**kwargs)

        event = self.get_event()
        context['event'] = event
        context['has_paid_lots'] = self.has_paid_lots()

        try:
            config = event.formconfig
        except AttributeError:
            config = FormConfig()

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
        )

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

            if lot.price > 0:
                return True

        return False

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization


class SubscriptionFormMixin(EventViewMixin, generic.FormView):
    success_message = None
    template_name = 'subscription/form.html'
    object = None
    subscription_form = None
    has_profile = False
    subscription_exists = False
    person_exists = False
    procceed = False

    def _subscription_exists(self):

        self.event = self.get_event()
        email = self.request.GET.get('email')

        if email:
            email = email.lower()
            self.procceed = True
            self.initial.update({'email': email})

            try:
                # Pessoa que possuem perfil, já logou (possui controle sobre
                # seus dados) e tem inscrição em algum dos eventos da
                # organização do evento atual.
                # @TODO PROBLEMA: Todos podem acessar os dados pelo e-mail.
                user = User.objects.get(
                    email=email,
                    last_login__isnull=False,
                )
                self.object = user.person
                self.has_profile = True
                self.person_exists = True

                return Subscription.objects.filter(
                    event=self.event,
                    person=self.object
                ).exists()

            except (User.DoesNotExist, AttributeError):

                try:
                    org_pks = [org.pk for org in self.organizations]
                    subscriptions = Subscription.objects.filter(
                        event__organization__in=org_pks,
                        person__email=email,
                    )

                    # @TODO ranking de mais completo em vez de pegar o primeiro
                    if subscriptions:
                        for sub in subscriptions:
                            if sub.event.pk == self.event.pk:
                                self.object = sub.person
                                self.person_exists = True
                                return True

                        self.object = subscriptions.first().person
                        self.person_exists = True

                except Subscription.DoesNotExist:
                    pass

        else:
            # Force to clear cache
            self.initial = {}

        return False

    def dispatch(self, request, *args, **kwargs):
        self.subscription_exists = self._subscription_exists()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        if not self.person_exists:
            return kwargs

        kwargs['instance'] = self.object

        if 'data' in kwargs and self.object and self.has_profile:
            data = {}

            model_data = model_to_dict(self.object)
            for key in six.iterkeys(model_data):
                value = model_data[key]

                if not value:
                    continue

                if isinstance(value, Model):
                    value = value.pk

                data.update({key: value})

            kwargs['data'].update(data)

        return kwargs

    def get_success_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def get_subscription_form(self):
        if self.subscription_form:
            return self.subscription_form

        return SubscriptionForm(event=self.get_event())

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt['has_profile'] = self.has_profile
        cxt['subscription_exists'] = self.subscription_exists
        cxt['procceed'] = self.procceed
        cxt['object'] = self.object

        # if self.is_by_lots():
        subscription_form = self.get_subscription_form()
        cxt['subscription_form'] = subscription_form

        non_field_errors = subscription_form.non_field_errors()

        if 'non_field_errors' in kwargs and non_field_errors:
            kwargs['non_field_errors'] += non_field_errors

        return cxt

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(
            form=self.get_form(),
            non_field_errors=form.non_field_errors()
        ))

    def form_valid(self, form):
        if self.success_message:
            messages.success(self.request, self.success_message)

        return super(SubscriptionFormMixin, self).form_valid(form)


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

        return query_set.filter(event=event)

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionListView, self).get_context_data(**kwargs)

        cxt.update({
            'can_add_subscription': self.can_add_subscription(),
            'lots': self.get_lots(),
            'has_filter': self.has_filter,
            'has_paid_lots': self.has_paid_lots(),
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


class SubscriptionViewFormView(EventViewMixin, generic.FormView):
    template_name = 'subscription/view.html'
    form_class = PersonForm
    subscription = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.subscription = get_object_or_404(
            Subscription,
            pk=self.kwargs.get('pk')
        )
        self.object = self.subscription.person

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object'] = self.object
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.object})
        kwargs.update({
            'is_chrome': 'chrome' in str(self.request.user_agent).lower()
        })

        try:
            kwargs['initial'].update({
                'city': '{}-{}'.format(self.object.city.name,
                                       self.object.city.uf)
            })
        except AttributeError:
            pass

        return kwargs


class SubscriptionAddFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """

    form_class = PersonForm
    success_message = 'Inscrição criada com sucesso.'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        form.setAsRequired('email')

        return form

    def can_access(self):
        event = self.get_event()
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            event
        )

        if event.subscription_type == event.SUBSCRIPTION_SIMPLE:
            return can_manage

        num_lots = self.get_num_lots()
        if num_lots == 0:
            self.permission_denied_message = \
                'Lote(s) não disponível(is).'

            self.permission_denied_url = reverse(
                'subscription:subscription-list',
                kwargs={'event_pk': event.pk}
            )

        return can_manage and num_lots > 0

    def post(self, request, *args, **kwargs):

        request.POST = request.POST.copy()

        def clear_string(field_name):
            if field_name not in request.POST:
                return

            value = request.POST.get(field_name)
            value = value.replace('.', '').replace('-', '').replace('/', '')

            request.POST[field_name] = value

        clear_string('cpf')
        clear_string('zip_code')

        confirmation_reply = request.POST.get('subscription_user_reply')
        confirmation_yes = request.POST.get('confirmation_yes')

        email = request.POST.get('email')
        person_form_kwargs = self.get_form_kwargs()

        if email:
            try:
                # Se há usuário que possui relacionamento com Person
                user = User.objects.get(email=email, person__isnull=False)

                if not confirmation_reply:
                    view = SubscriptionConfirmationView.as_view(
                        user=user,
                        submitted_data=request.POST,
                    )

                    return view(request, *args, **kwargs)

                elif confirmation_yes:
                    person_form_kwargs['instance'] = user.person

            except User.DoesNotExist:
                pass

        if self.is_by_lots():
            lot = request.POST.get('lot')
            del request.POST['lot']

        else:
            # Is internal lot
            lot = self.event.lots.get(internal=True)
            lot = lot.pk

        form_class = self.get_form_class()
        form = form_class(**person_form_kwargs)

        try:
            # 1 - Valida person form
            if form.is_valid():

                self.object = form.save()

                event = self.get_event()
                self.subscription_form = SubscriptionForm(
                    event=event,
                    data={
                        'lot': lot,
                        'person': self.object.pk,
                        'origin': Subscription.DEVICE_ORIGIN_WEB,
                        'created_by': request.user.pk,
                    }
                )

                # 2 - Valida subscription form
                if self.subscription_form.is_valid():
                    self.subscription_form.save()
                    response = self.form_valid(self.subscription_form)

                else:
                    response = self.form_invalid(self.subscription_form)

                return response

            else:
                return self.form_invalid(form)

        except Exception as e:
            messages.error(request, str(e))
            return self.render_to_response(self.get_context_data(
                form=form,
                non_field_errors=form.non_field_errors()
            ))


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


class SubscriptionAttendanceSearchView(EventViewMixin, generic.TemplateView):
    template_name = 'subscription/attendance.html'
    search_by = 'name'

    def get_permission_denied_url(self):
        return reverse('event:event-list')

    def get(self, request, *args, **kwargs):
        self.search_by = request.GET.get('search_by', 'name')
        return super(SubscriptionAttendanceSearchView, self).get(
            request,
            *args,
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        self.search_by = request.POST.get('search_by', 'name')
        value = request.POST.get('value')

        if value:
            kwargs.update({
                'result_by': self.search_by,
                'result': self.search_subscription(self.search_by, value),
            })

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionAttendanceSearchView, self).get_context_data(
            **kwargs
        )
        cxt.update({
            'attendances': self.get_attendances(),
            'search_by': self.search_by,
        })
        return cxt

    def get_attendances(self):
        try:
            return Subscription.objects.filter(
                attended=True,
                event=self.get_event(),
            ).order_by('-attended_on')

        except Subscription.DoesNotExist:
            return []

    def search_subscription(self, search_by, value):
        """ Busca inscrições de acordo com o valor passado. """
        method_name = 'search_by_{}'.format(search_by)
        method = getattr(self, method_name)
        return method(value)

    # noinspection PyMethodMayBeStatic
    def search_by_name(self, name):
        """ Busca inscrições por nome. """
        try:
            event = self.get_event()
            return event.subscriptions.filter(
                person__name__icontains=name.strip()
            )
        except Subscription.DoesNotExist:
            return []

    # noinspection PyMethodMayBeStatic
    def search_by_code(self, code):
        """ Busca inscrições por código. """
        try:
            event = self.get_event()
            return event.subscriptions.get(code=code.strip())
        except Subscription.DoesNotExist:
            return None

    # noinspection PyMethodMayBeStatic
    def search_by_email(self, email):
        """ Busca inscrições por email. """
        try:
            event = self.get_event()
            return event.subscriptions.get(person__email=email.strip())
        except Subscription.DoesNotExist:
            return None


class MySubscriptionsListView(AccountMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/my_subscriptions.html'
    ordering = ('event__name', 'event__date_start', 'event__date_end',)
    has_filter = False

    def get_permission_denied_url(self):
        return reverse('front:start')

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
            # event__published=True,
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        #
        # if self.get_paginate_by(self.object_list) is not None and hasattr(
        #         self.object_list, 'exists'):
        #     is_empty = not self.object_list.exists()
        # else:
        #     is_empty = len(self.object_list) == 0
        #
        # if is_empty:
        #     return redirect(reverse('event:event-list'))

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
        return queryset \
            .values(
            'event__name',
            'event__id',
        ) \
            .distinct() \
            .order_by('event__name')

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
    show_content_in_browser = False
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

    def can_access(self):
        return self.subscription.confirmed is True
