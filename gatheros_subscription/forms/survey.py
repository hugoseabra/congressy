""" Formulários de `Questionários/Surveys` """
from django import forms

from survey.services import SurveyService
from gatheros_subscription.models import EventSurvey


class EventSurveyForm(forms.Form):
    """ Formulário de survey. """

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)
        self.service = SurveyService(**kwargs)
        self.fields.update(self.service.fields)

        self.fields['name'].help_text = 'Nome do seu questionário. Exemplo ' \
                                        '"Estudantes" '
        self.fields['description'].help_text = 'Uma descrição para te ajudar' \
                                               ' a identificar este ' \
                                               'questionário. '
        self.fields['description'].widget = forms.Textarea(attrs={
            'cols': '20', 'rows': '2'
        })

    def is_valid(self):
        return super().is_valid() and self.service.is_valid()

    def save(self):
        survey = self.service.save()
        EventSurvey.objects.create(
            survey=survey,
            event=self.event
        )
        return survey
