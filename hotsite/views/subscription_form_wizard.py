from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from base.views import FormWizard
from gatheros_event.models import Event
from hotsite.views import StepOne, StepTwo, StepFive


class SubscriptionFormWizard(FormWizard):
    """
        View responsavel por decidir onde se inicia o process de inscrição
    """

    wizard_steps = {
        1: StepOne,
        2: StepTwo,
        5: StepFive,
    }

    persisting_steps = [StepTwo, StepFive]

    event = None

    def dispatch(self, request, *args, **kwargs):
        pre_flight = self.pre_flight(request=request)

        if pre_flight:
            return pre_flight

        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, step, **kwargs):

        form_wizard_context = super().get_context_data(**kwargs)
        step_context = step.get_context_data(**kwargs)

        # Merging contexts
        context = {**form_wizard_context, **step_context}

        return context

    def get(self, request, *args, **kwargs):

        """
            Se for evento com inscrição por lotes, ir para o step 1,
            caso contrario pode pular direto para o step 2.
        """
        if self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS:
            step_1 = StepOne()

            return render(request=request, template_name=step_1.template_name,
                          context=step_1.get_step_context_data(
                              event=self.event))
        else:
            raise NotImplementedError('error')

    def subscription_enabled(self):

        lots = self.get_lots()
        if len(lots) == 0:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def get_lots(self):
        return self.event.lots.filter(private=False)

    def post(self, request, *args, **kwargs):

        pre_flight = self.pre_flight(request=request)

        if pre_flight:
            return pre_flight

        post_data = request.POST.copy()

        super().post(request, *args, **kwargs)
        self.current_step(dirty_antecessor_data=post_data, event=self.event)

        form_class = self.current_step.form_class

        current_form = form_class(data=post_data,
                                  dependencies=self.current_step.dependency_artifacts)

        if current_form.is_valid():

            if self.current_step in self.persisting_steps:
                current_form.save()

            if self.next_step:

                next_step = self.next_step(
                    validated_antecessor_form=current_form,
                    event=self.event)

                if self.next_step == StepFive:



                    return redirect(next_step.redirect_url)

                return render(request=request,
                              template_name=next_step.template_name,
                              context=next_step.get_step_context_data(
                                  event=self.event))

        messages.error(request, 'Por favor corrigir os erros abaixo.')
        return render(request=request,
                      template_name=self.current_step.template_name,
                      context=self.current_step.get_step_context_data(
                          event=self.event, form=current_form))

    def pre_flight(self, request):

        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        self.event = get_object_or_404(Event, slug=slug)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()

        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        return None
