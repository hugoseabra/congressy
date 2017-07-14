from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from gatheros_event import forms
from gatheros_event.models import Organization
from gatheros_event.views.mixins import AccountMixin


class BaseEventView(AccountMixin, View):
    template_name = 'gatheros_event/event/form.html'
    success_message = ''
    success_url = None
    form_title = None

    def get_permission_denied_url(self):
        return reverse_lazy('event:event-list')

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        return super(BaseEventView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseEventView, self).get_context_data(**kwargs)
        context['next_path'] = self._get_referer_url()
        context['form_title'] = self.get_form_title()
        context['is_manager'] = self.has_internal_organization

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

    def get_object(self, queryset=None):
        """ Resgata objeto principal da view. """
        if self.object:
            return self.object

        self.object = super(BaseSimpleEditlView, self).get_object(queryset)
        return self.object

    def can_access(self):
        event = self.get_object()
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            event
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

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        return form_class(user=self.request.user, **self.get_form_kwargs())

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
            return super(EventAddFormView, self).post(request, *args, **kwargs)

    def get_initial(self):
        initial = super(EventAddFormView, self).get_initial()
        initial['organization'] = self.organization

        return initial

    def get_success_url(self):
        form = self.get_form()
        event = form.instance
        return reverse(
            'event:event-panel',
            kwargs={'pk': event.pk}
        )

    def can_access(self):
        return self.is_manager


class EventEditFormView(BaseSimpleEditlView, generic.UpdateView):
    form_class = forms.EventForm
    model = forms.EventForm.Meta.model
    success_url = reverse_lazy('event:event-list')
    success_message = 'Evento alterado com sucesso.'

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        return form_class(user=self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        initial = super(EventEditFormView, self).get_initial()
        initial['organization'] = self.organization

        return initial

    def get_success_url(self):
        form_kwargs = self.get_form_kwargs()
        data = form_kwargs.get('data', {})
        next_path = data.get('next')
        if next_path:
            return next_path

        return super(EventEditFormView, self).get_success_url()


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
