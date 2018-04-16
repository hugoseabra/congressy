from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from base.views import FormWizard
from gatheros_event.models import Event
from hotsite.views import StepOne, StepTwo


class SubscriptionFormWizard(FormWizard):
    """
        View responsavel por decidir onde se inicia o process de inscrição
    """

    wizard_steps = {
        1: StepOne,
        2: StepTwo,
    }

    event = None

    def dispatch(self, request, *args, **kwargs):
        self.pre_flight(request=request)
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

        self.pre_flight(request=request)

        super().post(request, *args, **kwargs)

        if not self.step:
            raise Exception('YOU AINT GOT NO STEP, STEP THE FUCK BACK')

        post_data = request.POST.copy()

        form = self.step.form_class(event=self.event, data=post_data)

        if form.is_valid():
            next_step = self.step.get_next_step(valid_form=form)
            return render(request=request,
                          template_name=next_step.template_name,
                          context=next_step.get_step_context_data(
                              event=self.event))

        messages.error(request, 'Por favor corriga os erros abaixo.')
        return render(request=request, template_name=self.step.template_name,
                      context=self.step.get_step_context_data(
                          event=self.event, form=form))

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
