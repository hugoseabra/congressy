from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin
from gatheros_subscription.models import Field, FieldOption
from .event_form import BaseFormFieldView


class FieldOptionAddView(AccountMixin, generic.View):
    http_method_names = ['post']

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        url = reverse('gatheros_event:event-list')

        try:
            field_pk = request.POST.get('field_pk')
            field = get_object_or_404(Field, pk=field_pk)
            name = request.POST.get('name')

            url = reverse('gatheros_subscription:field-options', kwargs={
                'event_pk': field.form.event.pk,
                'field_pk': field.pk
            })

            if not name:
                raise Exception('Informe um nome válido.')

            FieldOption.objects.create(field=field, name=name, value=name)

        except (Field.DoesNotExist, Exception) as e:
            messages.error(request, str(e))

        return redirect(url)


class FieldOptionEditView(AccountMixin, generic.View):
    http_method_names = ['post']

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        url = reverse('gatheros_event:event-list')

        try:
            pk = self.kwargs.get('pk')
            field_option = get_object_or_404(FieldOption, pk=pk)
            field = field_option.field

            name = request.POST.get('name')

            url = reverse('gatheros_subscription:field-options', kwargs={
                'event_pk': field.form.event.pk,
                'field_pk': field.pk
            })

            if not name:
                raise Exception('Informe um nome válido.')

            field_option.name = name
            field_option.value = name
            field_option.save()

        except (FieldOption.DoesNotExist, Exception) as e:
            messages.error(request, str(e))

        return redirect(url)


class FieldOptionDeleteView(DeleteViewMixin):
    model = FieldOption
    success_message = None
    http_method_names = ['post']

    def get_permission_denied_url(self):
        return self.get_success_url()

    def get_success_url(self):
        return reverse('gatheros_subscription:field-options', kwargs={
            'event_pk': self.object.field.form.event.pk,
            'field_pk': self.object.field.pk
        })

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
