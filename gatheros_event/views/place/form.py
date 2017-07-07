from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View, generic

from gatheros_event import forms
from gatheros_event.models import Organization
from gatheros_event.views.mixins import AccountMixin


class BaseFormView(AccountMixin, View):
    form_class = forms.PlaceForm
    template_name = 'gatheros_event/place/form.html'
    success_message = ''
    success_url = None
    form_title = None
    place_organization = None

    def dispatch(self, request, *args, **kwargs):

        if self.organization and not self._can_view():
            org = self.get_place_organization()
            messages.warning(
                request,
                'Você não tem permissão de realizar esta ação.'
            )
            return redirect(reverse(
                'event:organization-panel',
                kwargs={'pk': org.pk}
            ))

        return super(BaseFormView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        return super(BaseFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseFormView, self).get_context_data(**kwargs)
        context['next_path'] = self._get_referer_url()
        context['form_title'] = self.get_form_title()
        context['place_organization'] = self.get_place_organization()

        return context

    def _get_referer_url(self):
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
            previous_url = previous_url.replace(host, '')

            if previous_url != request.path:
                return previous_url

        return self.get_success_url()

    def get_form_title(self):
        return self.form_title

    def get_success_url(self):
        # noinspection PyUnresolvedReferences
        form_kwargs = self.get_form_kwargs()
        data = form_kwargs.get('data', {})
        next_path = data.get('next')
        if next_path:
            return next_path

        org = self.get_place_organization()
        return reverse('event:place-list', kwargs={
            'organization_pk': org.pk
        })

    def get_place_organization(self):
        if self.place_organization:
            return self.place_organization

        self.place_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.place_organization

    def _can_view(self):
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_places',
            self.get_place_organization()
        )
        return self.is_manager and can_manage


class PlaceAddFormView(BaseFormView, generic.CreateView):
    success_message = 'Local criado com sucesso.'
    form_title = 'Novo local'

    def get_initial(self):
        initial = super(PlaceAddFormView, self).get_initial()
        initial.update({
            'organization': self.get_place_organization()
        })
        return initial


class PlaceEditFormView(BaseFormView, generic.UpdateView):
    model = forms.PlaceForm.Meta.model
    success_message = 'Local alterado com sucesso.'
