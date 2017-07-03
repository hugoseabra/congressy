from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.models import Field, FieldOption
from gatheros_event.models import Event
from .event_form import BaseFormFieldView


class BaseFieldViewMixin(AccountMixin, generic.View):
    """ Mixin de view para FieldOption. """
    http_method_names = ['post']
    event = None
    field = None

    def get_success_url(self):
        """ URL de redirecionamento. """
        return reverse('gatheros_subscription:field-options', kwargs={
            'event_pk': self.event.pk,
            'field_pk': self.field.pk
        })

    def set_event(self, pk):
        """ Insere instância de Event. """
        self.event = get_object_or_404(Event, pk=pk)

    def set_field(self, pk):
        """ Insere instância de Field. """
        self.field = get_object_or_404(Field, pk=pk)


class FieldOptionAddView(BaseFieldViewMixin):
    """ View para adicionar FieldOption em Field. """

    def pre_dispatch(self, request):
        if request.method == 'POST':
            self.set_event(request.POST.get('event_pk'))
            self.set_field(request.POST.get('field_pk'))

        super(FieldOptionAddView, self).pre_dispatch(request)

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        url = reverse('gatheros_event:event-list')

        try:
            name = request.POST.get('name')

            if not name:
                raise Exception('Informe um nome válido.')

            FieldOption.objects.create(field=self.field, name=name, value=name)

        except (Field.DoesNotExist, Exception) as e:
            messages.error(request, str(e))

        return redirect(self.get_success_url())


class FieldOptionEditView(BaseFieldViewMixin):
    """ View para editar FieldOption em Field. """
    field_option = None

    def pre_dispatch(self, request):
        if request.method == 'POST':
            self.set_event(request.POST.get('event_pk'))
            
            pk = self.kwargs.get('pk')
            self.field_option = get_object_or_404(FieldOption, pk=pk)
            self.field = self.field_option.field

        super(FieldOptionEditView, self).pre_dispatch(request)

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        url = reverse('gatheros_event:event-list')

        try:
            name = request.POST.get('name')

            if not name:
                raise Exception('Informe um nome válido.')

            self.field_option.name = name
            self.field_option.save()

        except (FieldOption.DoesNotExist, Exception) as e:
            messages.error(request, str(e))

        return redirect(self.get_success_url())


class FieldOptionDeleteView(DeleteViewMixin):
    """ View para excluir FieldOption. """
    model = FieldOption
    event = None
    success_message = None
    http_method_names = ['post']

    def pre_dispatch(self, request):
        super(FieldOptionDeleteView, self).pre_dispatch(request)

        if request.method == 'POST':
            event_pk = request.POST.get('event_pk')
            self.event = get_object_or_404(Event, pk=event_pk)

    def get_success_url(self):
        """ URL de redirecionamento. """
        return reverse('gatheros_front:start')

    def get_permission_denied_url(self):
        return self.get_success_url()

    def can_delete(self):
        can_access = self.can_access()
        can_change = self.request.user.has_perm(
            'gatheros_subscription.change_field',
            self.object.field
        )

        return can_access and can_change


class FieldOptionsView(BaseFormFieldView):
    template_name = 'gatheros_subscription/event_form/field_options.html'
    form_title = 'Opções de Campo'

    def get_permission_denied_url(self):
        return reverse(
            'gatheros_subscription:fields-config',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def get_field(self):
        pk = self.kwargs.get('field_pk')
        return get_object_or_404(Field, pk=pk)

    def get_context_data(self, **kwargs):
        cxt = super(FieldOptionsView, self).get_context_data(**kwargs)

        field = self.get_field()
        cxt.update({
            'field': field,
            'options': field.options.all()
        })
        return cxt

    def can_access(self):
        can_access = super(FieldOptionsView, self).can_access()
        field = self.get_field()
        has_options = field.with_options
        if not has_options:
            messages.warning(
                self.request,
                'Este campo não possui suporte a opções.'
            )

        return can_access and has_options
