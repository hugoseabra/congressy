"""
    Formulário usado para pegar os dados solicitados pelo organizador da pessoa
    durante inscrições no hotsite
"""

from django import forms

from survey.directors import SurveyDirector


class SurveyForm(forms.Form):

    def __init__(self, event, user, event_survey, **kwargs):
        self.event_survey = event_survey
        self.event = event
        self.user = user

        survey_director = SurveyDirector(event=self.event, user=self.user)

        instance = survey_director.get_form(survey=self.event_survey.survey)
        super().__init__(**kwargs)
        self.initial = instance.initial
        self.fields = instance.fields
