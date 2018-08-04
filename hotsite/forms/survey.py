"""
    Formulário usado para pegar os dados solicitados pelo organizador da pessoa
    durante inscrições no hotsite
"""

from django import forms

from gatheros_subscription.directors import SubscriptionSurveyDirector


class SurveyForm(forms.Form):

    def __init__(self, subscription, survey, **kwargs):
        self.survey = survey
        self.subscription = subscription
            
        survey_director = SubscriptionSurveyDirector(self.subscription)
        data = kwargs.get('data')

        instance = survey_director.get_form(
            survey=self.survey,
            data=data,
        )
        super().__init__(**kwargs)
        self.initial = instance.initial
        self.fields = instance.fields
