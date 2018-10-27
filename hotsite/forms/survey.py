"""
    Formulário usado para pegar os dados solicitados pelo organizador da pessoa
    durante inscrições no hotsite
"""

from django import forms

from gatheros_subscription.directors import SubscriptionSurveyDirector


class SurveyForm(forms.Form):

    def __init__(self, subscription, event_survey, lot, **kwargs):

        survey_director = SubscriptionSurveyDirector(
            subscription=subscription,
            lot=lot,
        )

        instance = survey_director.get_active_form(
            survey=event_survey.survey
        )
        
        super().__init__(**kwargs)
        self.initial = instance.initial
        self.fields = instance.fields
