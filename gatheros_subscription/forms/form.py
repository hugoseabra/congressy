""" Formulários de `Form` """
from django import forms
from django.core.exceptions import PermissionDenied
from django.utils import six

from gatheros_subscription.models import Field, Form
from .field import FieldForm, FieldsRendererMixin


def _check_field_restriction(form, field):
    is_default = field.form_default_field is True
    is_active = field.active is True
    same_org = field.organization == form.event.organization

    if is_default or not is_active or not same_org:
        raise PermissionDenied('Este campo não pode ser adicionado.')


class EventFieldsForm(FieldsRendererMixin):
    """
    Formulário para construção de campos para o formulário do Django a partir
    do modelos `Field` de um modelo `Form` de evento.
    """

    def __init__(self, form, show_inactive=False, *args, **kwargs):
        """
        :type form: Form
        :type show_inactive: bool
        """

        self.form = form
        self.show_inactive = show_inactive
        super(EventFieldsForm, self).__init__(*args, **kwargs)

        self.set_required_fields()

    def _get_fields_queryset(self):
        fields_qs = self.form.fields.filter(active=True)
        inactive_list = self.form.get_inactive_fields_list()

        # Refaz retorno da lista de acordo com a ordem dos campos.
        field_ordered_list = []
        for field_name in self.form.get_order_list():
            if not self.show_inactive \
                    and inactive_list \
                    and field_name in inactive_list:
                continue

            for field in fields_qs:
                if field.name == field_name:
                    field_ordered_list.append(field)

        return field_ordered_list

    def set_required_fields(self):
        """ Define campos obrigatórios. """
        for field_name, field in six.iteritems(self.gatheros_fields):
            if self.form.is_required(field):
                self.set_attr(field_name, 'required', 'required')


class FormFieldForm(forms.Form):
    """ Formulário para gerenciar relação de `Field` com `Form`. """
    form = None

    def __init__(self, form, *args, **kwargs):
        self.form = form
        super(FormFieldForm, self).__init__(*args, **kwargs)

    def add_fields_by_names(self, fields_dict):
        """
        Adiciona campos através de um `dict` {`field_name`: `required`}
        :type fields_dict: dict
        """
        non_existing_fields = []
        for field_name, is_required in six.iteritems(fields_dict):
            try:
                self.add_field(field_name, is_required)

            except PermissionDenied:
                non_existing_fields.append(field_name)

        if non_existing_fields:
            raise PermissionDenied(
                'Os seguintes campos não puderam ser adicionados: {}'.format(
                    ', '.join(non_existing_fields)
                )
            )

    def add_new_field(self, data, required=None):
        """
        Cria campo a partir dos dados externos e adiciona ao `Form`.
        :type data: dict
        :type required: bool
            Define se campo é ou não obrigatório especificamente neste
            formulário. Caso seja `None`, prevalecerá o valor de `required`
            original de `Field`.
        """
        organization = self.form.event.organization
        field_form = FieldForm(organization=organization, data=data)

        _check_field_restriction(self.form, field_form.save(commit=False))
        field = field_form.save()

        self.add_field_by_instance(field, required)

        return field

    def add_field(self, field_name, required=None):
        """
        Adiciona relação de `Field` com o `Form`.
        :type field_name: str
        :type required: bool
            Define se campo é ou não obrigatório especificamente neste
            formulário. Caso seja `None`, prevalecerá o valor de `required`
            original de `Field`.
        """
        organization = self.form.event.organization
        try:
            field = organization.fields.get(name=field_name)

        except Field.DoesNotExist:
            raise PermissionDenied(
                'O campo `{}` não existe.'.format(field_name)
            )

        else:
            self.add_field_by_instance(field, required)

    def add_field_by_instance(self, field, required=None):
        """
        Adiciona relação de `Field` com o `Form`.
        :type field: Field
        :type required: bool
            Define se campo é ou não obrigatório especificamente neste
            formulário. Caso seja `None`, prevalecerá o valor de `required`
            original de `Field`.
        """
        _check_field_restriction(self.form, field)

        # Django não deixa acontecer duplicações
        self.form.fields.add(field)

        if required is not None and field.required != required:
            self._change_required_value(field)

        self._append_field_order(field)

    def activate(self, field):
        """ Ativa campo no formulário. """
        _check_field_restriction(self.form, field)
        self.form.activate_field(field)
        self.form.save()

    def deactivate(self, field):
        """ Desativa campo no formulário. """
        _check_field_restriction(self.form, field)
        self.form.deactivate_field(field)
        self.form.save()

    def set_as_required(self, field):
        """ Configura o campo como obrigatório. """
        config = self.form.required_configuration
        item = config.get(field.name) if config else None
        if not item and field.required is True:
            return

        if item and item is True:
            return

        self._change_required_value(field)

    def set_as_not_required(self, field):
        """ Configura o campo como não-obrigatório. """
        config = self.form.required_configuration
        item = config.get(field.name) if config else None

        if item and item is True:
            del config[field.name]

        config = config if config else {}

        if not item and field.required is True:
            config[field.name] = False

        self.form.required_configuration = config
        self.form.save()

    def _change_required_value(self, field):
        """
        Altera o campo como obrigatório ou não-obrigatório diferente do valor
        do campo `required` de `Field`.
        :param field: Field
        :return: None
        """
        config = self.form.required_configuration
        data = config if config else {}
        data.update({field.name: not field.required})

        self.form.required_configuration = data
        self.form.save()

    def _append_field_order(self, field):
        """
        Adicionar ordem de campo no final do formulário.
        :param field: Field
        :return: None
        """
        self.form.add_to_order(field)
        self.form.save()


class FormFieldOrderForm(forms.Form):
    """ Formulário para ordenação de campos em um formulário. """
    def __init__(self, form, *args, **kwargs):
        """
        :type form: Form
        :type field: Field
        """
        self.form = form
        super(FormFieldOrderForm, self).__init__(*args, **kwargs)

    def order_down(self, field):
        """
        Reordena o campo `Field` em uma posição anterior.
        :type field: Field
        """
        self._check_field_restriction(field)
        form_order = self.form.get_order_list()

        updated_order = []
        counter = 0
        for field_name in form_order:
            if field_name == field.name:
                previous = updated_order[counter - 1]
                if not previous:
                    continue

                # Campo atual assume valor do anterior
                updated_order[counter - 1] = field_name

                # Campo anterior assume valor do campo atual
                updated_order.append(previous)

                counter += 1
                continue

            updated_order.append(field_name)
            counter += 1

        self.form.set_order_list(updated_order)
        self.form.save()

    def order_up(self, field):
        """
        Reordena o campo `Field` em uma posição posterior.
        :type field: Field
        """

        self._check_field_restriction(field)
        form_order = self.form.get_order_list()

        updated_order = []
        next_field = None
        counter = 0

        for field_name in form_order:
            if field_name == field.name:
                next_field = form_order[counter + 1]
                if not next_field:
                    continue

                # Campo posterior assume valor do campo atual
                updated_order.append(next_field)

                # Campo atual assume valor do campo posteror
                updated_order.append(field_name)
                counter += 1
                continue

            # Já processado
            if field_name == next_field:
                continue

            updated_order.append(field_name)
            counter += 1

        self.form.set_order_list(updated_order)
        self.form.save()

    def _check_field_restriction(self, field):
        """ Verifica e valida restrições de `Field` para este formulário. """

        _check_field_restriction(self.form, field)

        if field.name not in [field.name for field in self.form.fields.all()]:
            raise PermissionDenied(
                'O campo `{}` não consta no formulário de o evento'
                ' `{}`.'.format(field.label, self.form.event.name)
            )
