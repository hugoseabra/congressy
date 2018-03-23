from collections import OrderedDict

from django import forms
from django.forms.fields import Field as DjangoField
from .field import SurveyField


class SurveyForm(forms.Form):
    """ Formulário Dinâmico. """
    """ Old kanuform """

    def __init__(self, survey, *args, **kwargs):
        self.survey = survey
        super(SurveyForm, self).__init__(*args, **kwargs)
        for question in self.survey.questions.all().order_by('order'):
            self.create_field(id=question.pk, name=question.name,
                              field_type=question.type,
                              label=question.label,
                              required=question.required,
                              question=question)

    def create_field(self, question, id, name, field_type, initial=None,
                     required=False,
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


        field = SurveyField(question, field_type, initial, required, label,
                            attrs={'data-id': id}, **kwargs)
        self.fields[name] = field.get_django_field()

        print('sdsada')