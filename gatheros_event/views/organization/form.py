from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from gatheros_event.helpers.account import update_account

from gatheros_event import forms
from gatheros_event.views.mixins import AccountMixin

from gatheros_event.helpers import account
from payment.tasks import create_pagarme_organizer_recipient
from payment.exception import OrganizerRecipientError


class BaseOrganizationView(AccountMixin, View):
    template_name = 'organization/form.html'
    success_message = ''
    success_url = None
    form_title = None

    def get_permission_denied_url(self):
        return reverse_lazy('event:organization-list')

    def get_form(self, form_class=None):
        """
        Retorna uma instancia de form para ser usada na view
        """
        if form_class is None:
            # noinspection PyUnresolvedReferences
            form_class = self.get_form_class()

        # noinspection PyUnresolvedReferences
        kwargs = self.get_form_kwargs()
        data = kwargs.get('data')
        internal = data.get('internal', False) if data else False

        return form_class(user=self.request.user, internal=internal, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        result = super(BaseOrganizationView, self).form_valid(form)

        update_account(
            request=self.request,
            organization=self.organization,
            force=True
        )

        return result

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

    def can_access(self):
        raise NotImplemented('Você deve implementar `can_access()`.')


class OrganizationAddFormView(BaseOrganizationView, generic.CreateView):
    form_class = forms.OrganizationForm
    success_message = 'Organização criada com sucesso.'
    form_title = 'Nova organização'

    def get_success_url(self):
        account.update_account(self.request, self.object)
        return reverse('event:event-list')

    def can_access(self):
        return True


class OrganizationAddInternalFormView(
    BaseOrganizationView,
    generic.CreateView
):
    form_class = forms.OrganizationForm
    success_message = 'Organização criada com sucesso.'
    form_title = 'Nova organização'

    def post(self, request, *args, **kwargs):
        try:
            person = request.user.person

            data = {'internal': True}
            data.update(person.get_profile_data())
            request.POST = data

            return super(OrganizationAddInternalFormView, self).post(
                request,
                *args,
                **kwargs
            )
        except ObjectDoesNotExist as e:
            raise PermissionDenied('Um error ocorreu: ' + str(e))

    # noinspection PyMethodMayBeStatic
    def get_success_url(self):
        return reverse_lazy('event:event-add')

    def can_access(self):
        return not self.has_internal_organization


class OrganizationEditFormView(BaseOrganizationView, generic.UpdateView):
    form_class = forms.OrganizationForm
    model = forms.OrganizationForm.Meta.model
    success_url = reverse_lazy('event:organization-list')
    success_message = 'Organização alterada com sucesso.'

    def can_access(self):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'editar'
        return context


class OrganizationFinancialEditFormView(OrganizationEditFormView):
    template_name = 'organization/financial-form.html'
    success_message = 'Informações bancárias salvas com sucesso.'
    success_url = reverse_lazy('event:event-list')
    form_class = forms.OrganizationFinancialForm

    def post(self, request, *args, **kwargs):

        response = super(OrganizationFinancialEditFormView, self).post(request,
                                                                       *args,
                                                                       **kwargs)

        form = self.get_form()
        if form.is_valid():
            try:
                create_pagarme_organizer_recipient(self.object)
            except OrganizerRecipientError:
                pass

        return response
