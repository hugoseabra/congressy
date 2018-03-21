from collections import OrderedDict

from django import forms
from django.forms.fields import Field as DjangoField
from .field import SurveyField


class SurveyForm(forms.Form):
    """ Formulário Dinâmico. """

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.survey_fields = OrderedDict()
        self.fields.keyOrder = []

    def create_field(self, name, field_type, initial=None, required=False,
                     label=None, **kwargs):
        """
        Cria um campo para o formulário conforme interface django field:
        field e widget.
        :param name: Nome do campo
        :param field_type: tipo do campo, conforme survey.fields.Field
        :param initial: valor inicial
        :param required: se obrigatório
        :param label: valor do rótulo
        :param kwargs: outros valores
        :rtype: DjangoField
        """
        field = SurveyField(field_type, initial, required, label, **kwargs)
        self.fields[name] = field.get_django_field()
        self.fields.keyOrder.append(name)
        self.survey_fields.update({name: field})

        return field.get_django_field()

    def set_attr(self, field_name, name, value):
        """
        Seta atributo em um campo do formulário.
        :param field_name: nome do campo
        :param name: nome do atributo
        :param value: valor do atributo
        """
        field = self.get_field_by_name(field_name)
        survey_field = self.survey_fields.get(field_name)
        if not field or not survey_field:
            return

        if name == 'required' and not survey_field.has_requirement():
            return

        field.widget.attrs.update({name: value})

    def unset_attr(self, field_name, name):
        """
        Remove atributo em um campo do formulário.
        :param field_name: nome do campo
        :param name: nome do atributo
        """
        field = self.get_field_by_name(field_name)
        attrs = field.widget.attrs
        attr = attrs.get(name)
        if attr:
            del attrs[name]

        field.widget.attrs = attrs

    def get_field_by_name(self, name):
        field = self.fields.get(name)
        if not field:
            raise Exception(
                'Não foi possível encontrar um campo com o nome'
                ' `{}`.'.format(name)
            )

        return field
