from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from gatheros_event import forms
from gatheros_event.views.mixins import AccountMixin


class PlaceAddView(AccountMixin, CreateView):
    form_class = forms.PlaceForm
    model = forms.PlaceForm.Meta.model
    template_name = 'gatheros_event/organization/form-place.html'
    success_url = reverse_lazy('gatheros_event:organization-panel')

    def get_initial(self):
        initial = super(PlaceAddView, self).get_initial()
        initial['organization'] = self.organization
        return initial

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(PlaceAddView, self).dispatch(request, *args, **kwargs)

        if not self._can_view():
            messages.warning(
                request,
                'Você não tem permissão para adicionar local.'
            )
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return dispatch

    def post(self, request, *args, **kwargs):
        next_path = request.POST.get('next')
        if next_path:
            self.success_url = next_path

        response = super(PlaceAddView, self).post(request, *args, **kwargs)
        messages.success(request, 'Local adicionado com sucesso.')
        return response

    def get_context_data(self, **kwargs):
        context = super(PlaceAddView, self).get_context_data(**kwargs)
        context['form_title'] = 'Adicionar novo local'
        context['next_path'] = self._get_referer_url()
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

    def get_success_url(self):
        previous = self._get_referer_url()
        if previous:
            return previous

        return self.success_url

    def _can_view(self):
        return self.request.user.has_perm(
            'gatheros_event.can_add_place',
            self.organization
        )
