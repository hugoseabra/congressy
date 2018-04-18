"""
    Formulário usado para pegar os dados solicitados pelo organizador da pessoa
    durante inscrições no hotsite
"""

from django import forms

from survey.directors import SurveyDirector


class SurveyForm(forms.Form):

    def __init__(self, **kwargs):

        self.event_survey = kwargs.get('initial').get('event_survey')
        self.event = kwargs.get('initial').get('event')
        self.user = kwargs.get('initial').get('user')

        survey_director = SurveyDirector(event=self.event,
                                         user=self.user)

        # # Resgata e poupua um novo form.
        # kwargs.update({'instance': survey_director.get_form(
        #     survey=self.event_survey.survey)})

        super().__init__(**kwargs)
        print('sdsdasd')