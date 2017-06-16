from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from gatheros_event.helpers.account import update_account

from gatheros_event import forms
from gatheros_event.views.mixins import AccountMixin


class BaseOrganizationView(AccountMixin, View):
    template_name = 'gatheros_event/organization/form.html'
    success_message = ''
    success_url = None
    form_title = None

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(BaseOrganizationView, self).dispatch(
            request,
            *args,
            **kwargs
        )
        if self.organization and not self.can_view():
            messages.warning(
                request,
                'Você não tem permissão de realizar esta ação.'
            )
            return redirect(reverse_lazy('gatheros_event:organization-list'))

        return dispatch

    def get_form(self, form_class=None):
        """
        Retorna uma instancia de form para ser usada na view
        """
        if form_class is None:
            # noinspection PyUnresolvedReferences
            form_class = self.get_form_class()

        # noinspection PyUnresolvedReferences
        return form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        return super(BaseOrganizationView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseOrganizationView, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['next_path'] = self._get_referer_url()
        context['form_title'] = self.get_form_title()

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

    def can_view(self):
        raise NotImplemented('Você deve implementar `can_view()`.')


class OrganizationAddFormView(BaseOrganizationView, generic.CreateView):
    form_class = forms.OrganizationForm
    success_message = 'Organização criada com sucesso.'
    form_title = 'Nova organização'

    def form_valid(self, form):
        result = super(OrganizationAddFormView, self).form_valid(form=form)
        update_account(
            request=self.request,
            organization=self.organization,
            force=True
        )
        return result

    def get_success_url(self):
        return reverse(
            'gatheros_event:organization-panel',
            kwargs={'pk': self.object.pk}
        )

    def can_view(self):
        return True


class OrganizationEditFormView(BaseOrganizationView, generic.UpdateView):
    form_class = forms.OrganizationForm
    model = forms.OrganizationForm.Meta.model
    success_url = reverse_lazy('gatheros_event:organization-list')
    success_message = 'Organização alterada com sucesso.'

    def can_view(self):
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_organization',
            self.get_object()
        )
        if not can_edit:
            messages.warning(
                self.request,
                "Você não tem permissão para editar esta organização."
            )

        return can_edit

    def get_success_url(self):
        form_kwargs = self.get_form_kwargs()
        data = form_kwargs.get('data', {})
        next_path = data.get('next')
        if next_path:
            return next_path

        return super(OrganizationEditFormView, self).get_success_url()
