from django.http.request import QueryDict
from django.views.generic import TemplateView

from base.exceptions import InvalidFormWizardStep


class FormWizard(TemplateView):
    wizard_steps = {}
    current_step = None
    next_step = None
    template_name = None
    event = None

    def post(self, request, *args, **kwargs):

        data = request.POST.copy()
        steps = {}

        steps['current_step'] = self._get_current_step(post_data=data)
        steps['next_step'] = self._get_next_step(post_data=data)

        for step in steps:

            if not steps[step]:
                msg = 'O passo(step) {} solicitado não existe.'.format(step)
                raise InvalidFormWizardStep(msg)

            self.current_step = self._get_helper_step(
                step_id=steps['current_step'])
            self.next_step = self._get_helper_step(step_id=steps['next_step'])

    def _get_helper_step(self, step_id: int):
        try:
            return self.wizard_steps[step_id]
        except KeyError:
            raise InvalidFormWizardStep('O passo(step) solicitado não existe.')

    @staticmethod
    def _get_next_step(post_data: QueryDict) -> int:

        next_step = post_data.get('next_step')

        if not next_step:
            raise InvalidFormWizardStep('Proximo passo(step) não informado.')

        return int(next_step)

    @staticmethod
    def _get_current_step(post_data: QueryDict) -> int:

        current_step = post_data.get('current_step')

        # Caveat: This will be interpreted as None and will raise an exception.
        if not current_step:
            raise InvalidFormWizardStep('Passo(step) atual não informado.')

        return int(current_step)
