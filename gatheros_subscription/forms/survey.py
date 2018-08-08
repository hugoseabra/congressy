""" Formulários de `Questionários/Surveys` """
from django import forms

from gatheros_subscription.models import EventSurvey
from survey.directors import SurveyDirector
from survey.services import SurveyService


class EventSurveyForm(forms.Form):
    """ Formulário de survey. """

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)
        self.service = SurveyService(**kwargs)
        self.fields.update(self.service.fields)

        self.fields['name'].help_text = \
            'Nome do seu questionário. Exemplo "Estudantes"'

        self.fields['description'].help_text = \
            'Uma descrição para te ajudar a identificar este questionário. '

        self.fields['description'].widget = forms.Textarea(attrs={
            'cols': '20',
            'rows': '2'
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


class SurveyForm(forms.Form):

    def __init__(self, event, event_survey, **kwargs):

        survey_director = SurveyDirector(event=event)

        super().__init__(**kwargs)

        instance = survey_director.get_form(survey=event_survey.survey)
        self.fields = instance.fields

    # def save(self):
    #
    #     survey_director = SurveyDirector(event=self.event)
    #
    #     lot = self.get_lot()
    #
    #     survey_form = survey_director.get_form(
    #         survey=lot.event_survey.survey,
    #         data=form_data.items()
    #     )
    #
    #     if survey_form.is_valid():
    #         survey_form.save_answers()
    #     else:
    #         raise Exception('SurveyAnswerForm was invalid: {}'.format(
    #             survey_form.errors
    #         ))
