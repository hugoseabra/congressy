import absoluteuri
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from core.util import model_field_slugify, ReservedSlugException
from gatheros_event import forms
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Organization, Event
from gatheros_event.views.mixins import AccountMixin


class BaseEventView(AccountMixin, View):
    template_name = 'event/form.html'
    success_message = ''
    success_url = None
    form_title = None
    event = None
    event_pk_field = 'pk'

    def pre_dispatch(self, request):
        self.event = self.get_event()

        if self.event:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().pre_dispatch(request)

    def get_permission_denied_url(self):
        return reverse_lazy('event:event-list')

    def get_event(self):
        if not self.event or self.event and not isinstance(self.event, Event):
            pk = self.kwargs.get(self.event_pk_field)
            if pk:
                self.event = Event.objects.get(pk=pk)

        return self.event

    def form_valid(self, form):
        try:
            response = super(BaseEventView, self).form_valid(form)
            update_account(
                request=self.request,
                organization=form.instance.organization,
                force=True
            )

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        else:
            messages.success(self.request, self.success_message)
            return response

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)

        context['next_path'] = self._get_referer_url()
        context['form_title'] = self.get_form_title()
        context['is_manager'] = self.has_internal_organization
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context

    def _get_referer_url(self):
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
            previous_url = previous_url.replace(host, '')

            if previous_url != request.path:
                return previous_url

        return self.success_url

    def get_form_title(self):
        return self.form_title


class BaseSimpleEditlView(BaseEventView):
    object = None

    def can_access(self):
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            self.event
        )
        if not can_edit:
            messages.warning(
                self.request,
                "Você não tem permissão para editar este evento."
            )

        return can_edit

    def get_success_url(self):
        event = self.get_object()
        url = reverse('event:event-panel', kwargs={'pk': event.pk})
        return url


class EventAddFormView(BaseEventView, generic.CreateView):
    form_class = forms.EventForm
    success_message = 'Evento criado com sucesso.'
    form_title = 'Novo evento'
    object = None

    def dispatch(self, request, *args, **kwargs):

        event_type = request.GET.get('event_type')
        if event_type and event_type not in (
                Event.EVENT_TYPE_FREE,
                Event.EVENT_TYPE_PAID,
                Event.EVENT_TYPE_SCIENTIFIC,
        ):
            messages.warning(request, 'Escolha um tipo de evento válido.')
            return redirect('event:event-add')

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        kwargs = self.get_form_kwargs()
        kwargs['lang'] = self.request.LANGUAGE_CODE

        return form_class(user=self.request.user, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['step'] = self.request.GET.get('step')
        context['event_type'] = self.request.GET.get('event_type')

        return context

    def post(self, request, *args, **kwargs):
        org_pk = request.POST.get('organization')
        try:
            org = Organization.objects.get(pk=org_pk)

            if not request.user.has_perm('gatheros_event.can_add_event', org):
                raise PermissionDenied()

        except (Organization.DoesNotExist, PermissionDenied):
            raise PermissionDenied(
                'Você não pode inserir um evento nesta organização.'
            )

        else:
            self.object = None
            form = self.get_form()
            if not form.is_valid():
                return self.render_to_response(self.get_context_data(
                    form=form,
                ))

            self.object = self.event = form.save()
            return self.form_valid(form)

    def get_initial(self):
        initial = super(EventAddFormView, self).get_initial()
        initial['organization'] = self.organization

        event_type = self.request.GET.get('event_type', Event.EVENT_TYPE_FREE)
        initial['event_type'] = event_type

        return initial

    def get_success_url(self):
        form = self.get_form()
        event = form.instance
        redirect_to = reverse_lazy('public:remarketing-redirect')
        page_type = '&page_type=new_event'
        next_page = '?next=' + reverse(
            'event:event-panel',
            kwargs={'pk': event.pk}
        )

        return redirect_to + next_page + page_type


class EventEditFormView(BaseSimpleEditlView, generic.UpdateView):
    template_name = 'event/form-edit-event.html'
    form_class = forms.EventForm
    model = forms.EventForm.Meta.model
    success_url = reverse_lazy('event:event-list')
    success_message = 'Evento alterado com sucesso.'

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        kwargs = self.get_form_kwargs()
        kwargs['lang'] = self.request.LANGUAGE_CODE

        return form_class(user=self.request.user, **kwargs)

    def get_initial(self):
        initial = super(EventEditFormView, self).get_initial()
        initial['organization'] = self.organization
        initial['date_start'] = self.event.date_start
        initial['date_end'] = self.event.date_end

        return initial

    def get_success_url(self):
        form = self.get_form()
        event = form.instance
        return reverse(
            'event:event-edit',
            kwargs={'pk': event.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'dados-do-evento'
        context['is_paid_event'] = \
            is_paid_event(self.get_event())

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = self.event = form.save()
            return self.form_valid(form)

        else:
            return self.render_to_response(self.get_context_data(
                form=form,
            ))


class EventPublicationFormView(BaseSimpleEditlView, generic.UpdateView):
    form_class = forms.EventPublicationForm
    model = forms.EventPublicationForm.Meta.model
    http_method_names = ['post']


class EventSubscriptionTypeFormView(BaseSimpleEditlView, generic.UpdateView):
    form_class = forms.EventEditSubscriptionTypeForm
    model = forms.EventEditSubscriptionTypeForm.Meta.model
    success_message = 'Tipo de inscrição alterada com sucesso.'
    form_title = 'Editar Tipo de Inscrição'


class EventDatesFormView(BaseSimpleEditlView, generic.UpdateView):
    form_class = forms.EventEditDatesForm
    model = forms.EventEditDatesForm.Meta.model
    success_message = 'Datas alteradas com sucesso.'
    form_title = 'Editar Datas do Evento'


class EventSlugUpdaterView(AccountMixin, generic.View):
    def get(self, request, *args, **kargs):
        name = request.GET.get('name')
        try:
            slug = model_field_slugify(
                model_class=Event,
                instance=Event(),
                string=name,
            )
            slug = str(slug)
            if slug is None or slug is 'none':
                slug = ''

            url = absoluteuri.build_absolute_uri('/{}'.format(slug))

            return HttpResponse(url)

        except ReservedSlugException as e:
            return HttpResponse(str(e), status=200)
