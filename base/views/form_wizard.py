
from django.http.request import QueryDict
from django.shortcuts import render_to_response
from django.views.generic import TemplateView


from base.exceptions import InvalidFormWizardStep


class FormWizard(TemplateView):
    wizard_steps = {}
    step = None
    template_name = None
    event = None

    def post(self, request, *args, **kwargs):

        data = request.POST.copy()

        step_id = self._get_step(post_data=data)
        step_class = None

        if step_id:
            step_class = self._get_helper_step(step_id=step_id)

        if step_class:
            self.step = step_class(event=self.event)



        """
         How does the wizard work?
         
         On GET:
            - Call the first step. 
            - Let the step take care of return some kind of HttpResponse.
         
         On POST's:
        
            - Verifies if we even have a step, if not send back to first 
            form step, if we have a step number, verify that it is valid. 
            
                - If not:
                    - Call the first step. 
            
            - Call the given step passing in all the request data. 
            
            -  Let the step take care of return some kind of HttpResponse.
            
            
        
            
         
         
        
        """





        # context = step.get_context_data()
        #
        # return render_to_response(template_name=step.template_name,
        #                           context=context)



        # if not self._post_checker(post_data=data):
        #     raise InvalidFormWizardStep()
        #

        #
        # step = step(self, **kwargs)
        #
        # step_context = step.get_context()
        #
        # # Every step needs a new form.
        # if not step.validate():
        #     step_context['form'] = step.get_form_instance()
        #
        # return render_to_response(template_name=step.template,
        #                           context=step_context)

    def _post_checker(self, post_data: QueryDict) -> bool:

        suspect_step = self._get_step(post_data=post_data)

        if not suspect_step:
            return False

        if not self._does_step_belong_to_wizard(suspect_step=suspect_step):
            return False

        if not self._post_data_has_required_references(post_data=post_data,
                                                       step=suspect_step):
            return False

        return True

    def _get_helper_step(self, step_id: int):
        return self.wizard_steps[step_id]

    def _does_step_belong_to_wizard(self, suspect_step: int) -> bool:

        if suspect_step not in self.wizard_steps:
            return False

        return True

    def _post_data_has_required_references(self, post_data: QueryDict,
                                           step: int, **kwargs) -> bool:

        step_instance = self.wizard_steps[step](kwargs)

        for dependency in step_instance.dependes_on:

            if dependency not in post_data:
                return False

        return True

    @staticmethod
    def _get_step(post_data: QueryDict) -> int:

        next_step = post_data.get('next_step')
        previous_step = post_data.get('previous_step')

        # Caveat: This will be interpreted as None and will raise an exception.
        if not next_step and not previous_step:
            return 0

        suspect_step_string = next_step if next_step else previous_step

        return int(suspect_step_string)
