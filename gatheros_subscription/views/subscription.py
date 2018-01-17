from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import generic

from gatheros_event.models import Event, Person
from gatheros_event.views.mixins import (
    AccountMixin,
    DeleteViewMixin,
    FormListViewMixin,
)
from gatheros_event.forms import PersonForm
from gatheros_subscription.forms import SubscriptionForm
from gatheros_subscription.helpers.subscription import \
    export as subscription_export
from gatheros_subscription.models import Subscription
from .filters import SubscriptionFilterForm


class EventViewMixin(AccountMixin, generic.View):
    """ Mixin de view para vincular com informações de event. """
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.permission_denied_url = reverse(
            'event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')}
        )
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)

        event = self.get_event()
        context['event'] = event

        try:
            context['config'] = event.formconfig
        except AttributeError:
            context['config'] = {}

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

    def get_lots(self):
        return self.get_event().lots.filter(
            internal=False
        )

    def get_num_lots(self):
        """ Recupera número de lotes a serem usados nas inscrições. """
        lot_qs = self.get_lots()
        return lot_qs.count() if lot_qs else 0


class SubscriptionFormMixin(EventViewMixin, generic.FormView):
    success_message = None
    template_name = 'gatheros_subscription/subscription/form.html'
    object = None

    def get_success_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(SubscriptionFormMixin, self).form_invalid(form)

    def form_valid(self, form):
        try:
            self.object = form.save()

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        else:
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


class SubscriptionAddFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """

    form_class = PersonForm
    # template_name = 'gatheros_subscription/subscription/form.html'
    template_name = 'subscription/form.html'
    success_message = 'Inscrição criada com sucesso.'

    def can_access(self):
        event = self.get_event()
        enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            event
        ) if enabled else False

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


class SubscriptionConfirmationView(EventViewMixin, generic.TemplateView):
    subscription_user = None
    submitted_data = None
    # template_name = 'gatheros_subscription/subscription/subscription_confirmation.html'
    template_name = 'subscription/subscription_confirmation.html'
    @classonlymethod
    def as_view(cls, user, submitted_data, **initkwargs):

        del submitted_data['user']

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


# class SubscriptionEditFormView(SubscriptionAddFormView):
#     object = None
#     success_message = 'Inscrição alterada com sucesso.'
#
#     def dispatch(self, request, *args, **kwargs):
#         self.object = get_object_or_404(Subscription, pk=self.kwargs.get('pk'))
#
#         return super(SubscriptionEditFormView, self).dispatch(
#             request,
#             *args,
#             **kwargs
#         )
#
#     def post(self, request, *args, **kwargs):
#         # Pula confirmação
#         return super(SubscriptionAddFormView, self).post(
#             request,
#             *args,
#             **kwargs
#         )
#
#     def get_form_kwargs(self):
#         kwargs = super(SubscriptionEditFormView, self).get_form_kwargs()
#         kwargs.update({'instance': self.object})
#
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         cxt = super(SubscriptionEditFormView, self).get_context_data(**kwargs)
#         cxt.update({
#             'object': self.object
#         })
#
#         return cxt
#
#     def can_access(self):
#         event = self.get_event()
#         enabled = event.subscription_type != event.SUBSCRIPTION_DISABLED
#         return self.request.user.has_perm(
#             'gatheros_event.can_manage_subscriptions',
#             event
#         ) if enabled else False


class SubscriptionDeleteView(EventViewMixin, DeleteViewMixin):
    template_name = 'subscription/delete.html'
    model = Subscription
    success_message = 'Inscrição excluída com sucesso.'
    place_organization = None

    def get_permission_denied_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def get_success_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def can_delete(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )


class SubscriptionAttendanceSearchView(EventViewMixin, generic.TemplateView):
    template_name = 'subscription/attendance.html'
    search_by = 'name'

    def get_permission_denied_url(self):
        return reverse(
            'event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')},
        )

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


# class SubscriptionAttendanceView(EventViewMixin, generic.FormView):
#     form_class = SubscriptionAttendanceForm
#     http_method_names = ['post']
#     search_by = 'name'
#     register_type = None
#     object = None
#
#     def get_object(self):
#         if self.object:
#             return self.object
#
#         try:
#             self.object = Subscription.objects.get(pk=self.kwargs.get('pk'))
#
#         except Subscription.DoesNotExist:
#             return None
#
#         else:
#             return self.object
#
#     def get_success_url(self):
#         url = reverse(
#             'subscription:subscription-attendance-search',
#             kwargs={'event_pk': self.kwargs.get('event_pk')}
#         )
#         if self.search_by is not None and self.search_by != 'name':
#             url += '?search_by=' + str(self.search_by)
#
#         return url
#
#     def get_permission_denied_url(self):
#         return self.get_success_url()
#
#     def get_form_kwargs(self):
#         kwargs = super(SubscriptionAttendanceView, self).get_form_kwargs()
#         kwargs.update({'instance': self.get_object()})
#         return kwargs
#
#     def form_invalid(self, form):
#         messages.error(self.request, form.errors)
#         return super(SubscriptionAttendanceView, self).form_invalid(form)
#
#     def form_valid(self, form):
#         sub = self.get_object()
#
#         try:
#             if self.register_type is None:
#                 raise Exception('Nenhuma ação foi informada.')
#
#             register_name = 'Credenciamento' \
#                 if self.register_type == 'register' \
#                 else 'Cancelamento de credenciamento'
#
#         except Exception as e:
#             form.add_error(None, str(e))
#             return self.form_invalid(form)
#
#         else:
#             messages.success(
#                 self.request,
#                 '{} de `{}` registrado com sucesso.'.format(
#                     register_name,
#                     sub.person.name
#                 )
#             )
#             form.attended(self.register_type == 'register')
#             return super(SubscriptionAttendanceView, self).form_valid(form)
#
#     def post(self, request, *args, **kwargs):
#         self.search_by = request.POST.get('search_by')
#         self.register_type = request.POST.get('action')
#
#         return super(SubscriptionAttendanceView, self).post(
#             request,
#             *args,
#             **kwargs
#         )
#
#     def can_access(self):
#         event = self.get_event()
#         sub = self.get_object()
#         return sub.event.pk == event.pk


class MySubscriptionsListView(AccountMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    # template_name = 'gatheros_subscription/subscription/my_subscriptions.html'
    template_name = 'subscription/my_subscriptions.html'
    ordering = ('event__name', 'event__date_start', 'event__date_end',)
    has_filter = False

    def get_permission_denied_url(self):
        return reverse('front:start')

    def get_queryset(self):
        person = self.request.user.person
        query_set = super(MySubscriptionsListView, self).get_queryset()

        notcheckedin = self.request.GET.get('notcheckedin')
        if notcheckedin:
            query_set = query_set.filter(attended=False)
            self.has_filter = True

        pastevents = self.request.GET.get('pastevents')
        now = datetime.now()
        if pastevents:
            query_set = query_set.filter(event__date_end__lt=now)
            self.has_filter = True

        else:
            query_set = query_set.filter(event__date_start__gt=now)

        return query_set.filter(
            person=person,
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


class SubscriptionExportView(AccountMixin, FormListViewMixin):
    # template_name = 'gatheros_subscription/subscription/attendance.html'
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

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt.update({
            'event': self.get_event()
        })
        return cxt

    def get_form_kwargs(self):
        kwargs = super(SubscriptionExportView, self).get_form_kwargs()
        kwargs.update({
            'event': self.kwargs.get('event_pk')
        })
        return kwargs

    def get_queryset(self):
        queryset = Subscription.objects \
            .filter(event__pk=self.kwargs.get('event_pk'))

        form = self.get_form()
        if form.is_valid():
            queryset = form.filter(queryset)

        return queryset

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'xls':
            # Chamando exportação
            output = subscription_export(self.get_queryset())

            # Criando resposta http com arquivo de download
            response = HttpResponse(output,
                                    content_type="application/vnd.ms-excel")

            # Definindo nome do arquivo
            event = self.get_event()
            name = "%s-%s.xls" % (event.pk, event.slug)
            response['Content-Disposition'] = 'attachment; filename=%s' % name

            return response

        return super(SubscriptionExportView, self).get(request, *args,
                                                       **kwargs)

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            Event.objects.get(pk=self.kwargs.get('event_pk'))
        )
