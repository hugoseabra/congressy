from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.forms import FieldOptionForm
from gatheros_subscription.models import Field, FieldOption


class BaseFieldOptionViewMixin(AccountMixin, generic.TemplateView):
    """ Mixin de view para FieldOption. """
    form_title = 'Opções de Campo'
    field = None

    def get_field(self):
        """ Resgata instância de `Field` a partir da QueryString """
        if self.field:
            return self.field

        self.field = get_object_or_404(Field, pk=self.kwargs.get('field_pk'))
        return self.field

    def get_context_data(self, **kwargs):
        cxt = super(BaseFieldOptionViewMixin, self).get_context_data(**kwargs)
        cxt.update({
            'form_title': self.form_title,
            'field': self.get_field(),
            'options': self.get_field().options.all().order_by('pk')
        })
        return cxt

    def can_access(self):
        if not self.field.with_options:
            self.permission_denied_message = \
                'Este campo não possui suporte a opções.'
            return False

        organization = self.field.organization
        is_member = organization.is_member(self.request.user)
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_fields',
            organization
        )
        is_default = self.field.form_default_field

        return self.is_manager and is_member and can_manage and not is_default

    def get_success_url(self):
        raise NotImplementedError()

    def get_permission_denied_url(self):
        raise NotImplementedError()


# noinspection PyAbstractClass
class BaseFieldOptionFormViewMixin(BaseFieldOptionViewMixin):
    """ Base para views de formulário de `FieldOption` """
    http_method_names = ['post']
    form_class = FieldOptionForm
    object = None

    def pre_dispatch(self, request):
        if request.method == 'GET':
            raise PermissionDenied(self.get_permission_denied_message())

        super(BaseFieldOptionFormViewMixin, self).pre_dispatch(request)

    def get_object(self, queryset=None):
        if self.object:
            return self.object

        parent = super(BaseFieldOptionFormViewMixin, self)
        # noinspection PyUnresolvedReferences
        self.object = parent.get_object(queryset)
        return self.object

    def get_form_kwargs(self):
        parent = super(BaseFieldOptionFormViewMixin, self)
        # noinspection PyUnresolvedReferences
        kwargs = parent.get_form_kwargs()
        kwargs.update({'field': self.field})
        return kwargs

    # noinspection PyUnusedLocal
    def form_invalid(self, form):
        return redirect(self.get_success_url())


# noinspection PyAbstractClass
class FieldOptionsView(BaseFieldOptionViewMixin, generic.TemplateView):
    """ View para gerenciar `FieldOption`"""
    template_name = \
        'gatheros_subscription/field/field_options.html'

    def pre_dispatch(self, request):
        self.field = self.get_field()
        super(FieldOptionsView, self).pre_dispatch(request)

    def get_permission_denied_url(self):
        return reverse(
            'subscription:fields',
            kwargs={'organization_pk': self.field.organization.pk}
        )


class FieldOptionAddView(
    BaseFieldOptionFormViewMixin,
    generic.CreateView
):
    """ View para adicionar `FieldOption` """

    def pre_dispatch(self, request):
        if request.method == 'POST':
            self.field = get_object_or_404(
                Field,
                pk=request.POST.get('field_pk')
            )

        super(FieldOptionAddView, self).pre_dispatch(request)

    def get_success_url(self):
        return reverse('subscription:field-options', kwargs={
            'field_pk': self.field.pk
        })

    def get_permission_denied_url(self):
        return reverse('front:start')


class FieldOptionEditView(
    BaseFieldOptionFormViewMixin,
    generic.UpdateView
):
    """ View para editar FieldOption em Field. """
    model = BaseFieldOptionFormViewMixin.form_class.Meta.model

    def pre_dispatch(self, request):
        self.object = self.get_object()
        self.field = self.object.field
        super(FieldOptionEditView, self).pre_dispatch(request)

    def get_success_url(self):
        return reverse('subscription:field-options', kwargs={
            'field_pk': self.field.pk
        })

    def get_permission_denied_url(self):
        return reverse('subscription:fields', kwargs={
            'organization_pk': self.field.organization.pk
        })


class FieldOptionDeleteView(
    BaseFieldOptionViewMixin,
    DeleteViewMixin
):
    """ View para excluir `FieldOption`. """
    model = FieldOption
    field = None
    success_message = None
    http_method_names = ['post']

    def pre_dispatch(self, request):
        self.object = self.get_object()
        self.field = self.object.field
        super(FieldOptionDeleteView, self).pre_dispatch(request)

    def get_success_url(self):
        return reverse('subscription:field-options', kwargs={
            'field_pk': self.field.pk
        })

    def get_permission_denied_url(self):
        return reverse('subscription:fields', kwargs={
            'organization_pk': self.field.organization.pk
        })

    def can_delete(self):
        return True
