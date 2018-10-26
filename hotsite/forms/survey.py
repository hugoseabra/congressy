"""
    Formulário usado para pegar os dados solicitados pelo organizador da pessoa
    durante inscrições no hotsite
"""

from django import forms

from gatheros_subscription.directors import SubscriptionSurveyDirector


class SurveyForm(forms.Form):

    def __init__(self, subscription, event_survey, **kwargs):

        survey_director = SubscriptionSurveyDirector(
            subscription=subscription,
        )

        instance = survey_director.get_active_form(
            survey=event_survey.survey
        )
        
        super().__init__(**kwargs)
        self.initial = instance.initial
        self.fields = instance.fields
