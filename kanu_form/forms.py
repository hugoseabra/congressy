from collections import OrderedDict

from django import forms
from django.forms.fields import Field as DjangoField

from .field import Field as KanuField


class KanuForm(forms.Form):
    """ Formulário Dinâmico. """

    def __init__(self, *args, **kwargs):
        super(KanuForm, self).__init__(*args, **kwargs)
        self.kanu_fields = OrderedDict()
        self.fields.keyOrder = []

    def create_field(self, name, field_type, initial=None, required=True,
                     label=None, **kwargs):
        """
        Cria um campo para o formulário conforme interface django field:
        field e widget.
        :param name: Nome do campo
        :param field_type: tipo do campo, conforme kanu_form.fields.field.Field
        :param initial: valor inicial
        :param required: se obrigatório
        :param label: valor do rótulo
        :param kwargs: outros valores
        :rtype: DjangoField
        """
        field = KanuField(field_type, initial, required, label, **kwargs)
        self.fields[name] = field.get_django_field()
        self.fields.keyOrder.append(name)
        self.kanu_fields.update({name: field})

        return field.get_django_field()
