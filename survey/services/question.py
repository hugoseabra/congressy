"""
Application Service
"""
from survey.services import mixins
from survey.managers import QuestionManager
from survey.models import Survey


class QuestionService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = QuestionManager

    def clean_survey(self):
        survey = self.cleaned_data.get('survey')
        if survey:
            try:
                survey = Survey.objects.get(pk=survey)
            except Survey.DoesNotExist:
                mixins.forms.ValidationError(
                    'Questionário não informado ou inválido.'
                )

        return survey

    def _get_manager_kwargs(self, **kwargs):
        kwargs = super()._get_manager_kwargs(**kwargs)
        kwargs['survey'] = self.cleaned_data.get('survey')
        return kwargs
