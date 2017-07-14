from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Organization
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.forms import FieldForm, OrganizationFieldsForm
from gatheros_subscription.models import Field


class BaseFieldsView(AccountMixin, generic.View):
    """ Base para classes de view de `OrganizationFields`"""
    success_message = None
    fields_organization = None

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        return super(BaseFieldsView, self).form_valid(form)

    def get_success_url(self):
        return reverse('subscription:fields', kwargs={
            'organization_pk': self.fields_organization.pk
        })

    def can_access(self):
        is_member = self.fields_organization.is_member(self.request.user)

        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_fields',
            self.fields_organization
        )

        return self.is_manager and is_member and can_manage

    def get_next_path(self):
        """
        Resgata se após o post a view será redirecionada para uma URL
        específica.
        """
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')

        if not previous_url:
            return None

        host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
        previous_url = previous_url.replace(host, '')

        return previous_url if previous_url != request.path else None


class FieldsListView(BaseFieldsView, generic.FormView):
    """ View de Lista de campos da organização. """

    template_name = 'gatheros_subscription/field/fields.html'
    form_class = OrganizationFieldsForm

    def get_fields_organization(self):
        """ Resgata instância de organização da view """
        if self.fields_organization:
            return self.fields_organization

        self.fields_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )

        return self.fields_organization

    def pre_dispatch(self, request):
        self.fields_organization = self.get_fields_organization()
        super(FieldsListView, self).pre_dispatch(request)

    def get_form_kwargs(self):
        kwargs = super(FieldsListView, self).get_form_kwargs()
        kwargs.update({
            'organization': self.get_fields_organization()
        })
        return kwargs

    def get_context_data(self, **kwargs):
        cxt = super(FieldsListView, self).get_context_data(**kwargs)
        cxt.update({'fields_organization': self.get_fields_organization()})
        return cxt


class FieldsAddView(BaseFieldsView, generic.CreateView):
    """ View para adicionar campo em organização. """

    form_class = FieldForm
    template_name = 'gatheros_subscription/field/form.html'
    success_message = 'Campo criado com sucesso.'

    def get_fields_organization(self):
        """ Resgata instância de organização da view """
        if self.fields_organization:
            return self.fields_organization

        self.fields_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )

        return self.fields_organization

    def pre_dispatch(self, request):
        self.fields_organization = self.get_fields_organization()
        super(FieldsAddView, self).pre_dispatch(request)

    def get_permission_denied_url(self):
        return reverse(
            'event:organization-panel',
            kwargs={'pk': self.kwargs.get('organization_pk')}
        )

    def get_form_kwargs(self):
        kwargs = super(FieldsAddView, self).get_form_kwargs()
        kwargs.update({'organization': self.fields_organization})
        return kwargs

    def get_context_data(self, **kwargs):
        cxt = super(FieldsAddView, self).get_context_data(**kwargs)
        cxt.update({
            'form_title': 'Novo Campo',
            'field_organization': self.fields_organization,
        })
        return cxt


class FieldsEditView(BaseFieldsView, generic.UpdateView):
    """ View para adicionar campo em organização. """

    form_class = FieldForm
    model = FieldForm.Meta.model
    template_name = 'gatheros_subscription/field/form.html'
    success_message = 'Campo alterado com sucesso.'
    object = None

    def get_object(self, queryset=None):
        if self.object:
            return self.object

        self.object = super(FieldsEditView, self).get_object(queryset)
        return self.object

    def pre_dispatch(self, request):
        self.object = self.get_object()
        self.fields_organization = self.object.organization
        super(FieldsEditView, self).pre_dispatch(request)

    def get_form_kwargs(self):
        kwargs = super(FieldsEditView, self).get_form_kwargs()
        kwargs.update({'organization': self.fields_organization})
        return kwargs

    def post(self, request, *args, **kwargs):
        next_path = request.POST.get('next_path')
        response = super(FieldsEditView, self).post(request, *args, **kwargs)
        if next_path:
            return redirect(next_path)

        return response

    def get_context_data(self, **kwargs):
        cxt = super(FieldsEditView, self).get_context_data(**kwargs)
        cxt.update({
            'form_title': 'Editar Campo',
            'field_organization': self.fields_organization,
            'next_path': self.get_next_path()
        })
        return cxt


class FieldsDeleteView(BaseFieldsView, DeleteViewMixin):
    """ View de remoção de campo de organização. """
    model = Field
    success_message = 'Campo excluído com sucesso.'

    def get_object(self, queryset=None):
        if self.object:
            return self.object

        parent = super(FieldsDeleteView, self)
        self.object = parent.get_object(queryset)
        return self.object

    def pre_dispatch(self, request):
        self.object = self.get_object()
        self.fields_organization = self.object.organization
        super(FieldsDeleteView, self).pre_dispatch(request)

    def get_delete_message(self):
        msg = 'Tem certeza que deseja excluir o campo "{label}"?'

        num_answers = self.object.answers.count()
        if num_answers > 0:
            msg += ' Este campo possui {num_answers} inscrições vinculadas que'
            msg += ' serão perdidas irreversivelmente. '

        return msg.format(
            label=self.object.label,
            num_answers=num_answers
        )

    def get_permission_denied_url(self):
        return self.get_success_url()

    def can_delete(self):
        can_delete = super(FieldsDeleteView, self).can_delete()
        return can_delete and self.object.form_default_field is False
