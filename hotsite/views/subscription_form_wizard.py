from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect
from hotsite.views.mixins import EventMixin
from hotsite import forms
from gatheros_subscription.models import Lot


FORMS = [("lot", forms.LotsForm),
         ("person", forms.SubscriptionPersonForm),
         ("payment", forms.PaymentForm)]

TEMPLATES = {"lot": "hotsite/lot_form.html",
             "person": "hotsite/person_form.html",
             "payment": "hotsite/payment_form.html"}


def is_paid_lot(wizard):
    """Return true if user opts for  a paid lot"""

    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('lot') or {'lots': 'none'}

    # Return true if lot has price and price > 0
    lot = cleaned_data['lots']

    if isinstance(lot, Lot):
        if lot.price and lot.price > 0:
            return True

    return False


class SubscriptionWizardView(EventMixin, SessionWizardView):

    condition_dict = {'payment': is_paid_lot}

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        raise Exception('fuck me its 02:04 AM')

        # this runs for the step it's on as well as for the step before
    def get_form_initial(self, step):

            if step == 'lot':
                return self.initial_dict.get(step, {'event': self.event})

            # get the data for step person from  step lot
            if step == 'person':
                prev_data = self.storage.get_step_data('lot')
                lot = prev_data.get('lot-lots', '')
                return self.initial_dict.get(step, {
                    'lot': lot,
                    'event': self.event,
                })

            return self.initial_dict.get(step, {})


# class SubscriptionFormWizard(FormWizard):
#     """
#         View responsavel por decidir onde se inicia o process de inscrição
#     """
#
#     wizard_steps = {
#         1: StepOne,
#         2: StepTwo,
#         5: StepFive,
#     }
#
#     persisting_steps = [StepTwo, StepFive]
#
#     event = None
#
#     def dispatch(self, request, *args, **kwargs):
#         pre_flight = self.pre_flight(request=request)
#
#         if pre_flight:
#             return pre_flight
#
#         response = super().dispatch(request, *args, **kwargs)
#         return response
#
#     def get_context_data(self, step, **kwargs):
#
#         form_wizard_context = super().get_context_data(**kwargs)
#         step_context = step.get_context_data(**kwargs)
#
#         # Merging contexts
#         context = {**form_wizard_context, **step_context}
#
#         return context
#
#     def get(self, request, *args, **kwargs):
#
#         """
#             Se for evento com inscrição por lotes, ir para o step 1,
#             caso contrario pode pular direto para o step 2.
#         """
#         if self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS:
#             step_1 = StepOne()
#
#             return render(request=request, template_name=step_1.template_name,
#                           context=step_1.get_step_context_data(
#                               event=self.event))
#         else:
#             raise NotImplementedError('error')
#
#     def subscription_enabled(self):
#
#         lots = self.get_lots()
#         if len(lots) == 0:
#             return False
#
#         return self.event.status == Event.EVENT_STATUS_NOT_STARTED
#
#     def get_lots(self):
#         return self.event.lots.filter(private=False)
#
#     def post(self, request, *args, **kwargs):
#
#         pre_flight = self.pre_flight(request=request)
#
#         if pre_flight:
#             return pre_flight
#
#         post_data = request.POST.copy()
#
#         super().post(request, *args, **kwargs)
#         self.current_step(dirty_antecessor_data=post_data, event=self.event)
#
#         form_class = self.current_step.form_class
#
#         current_form = form_class(data=post_data,
#                                   dependencies=self.current_step.dependency_artifacts)
#
#         if current_form.is_valid():
#
#             if self.current_step in self.persisting_steps:
#                 current_form.save()
#
#             if self.next_step:
#
#                 next_step = self.next_step(
#                     validated_antecessor_form=current_form,
#                     event=self.event)
#
#                 if self.next_step == StepFive:
#
#
#
#                     return redirect(next_step.redirect_url)
#
#                 return render(request=request,
#                               template_name=next_step.template_name,
#                               context=next_step.get_step_context_data(
#                                   event=self.event))
#
#         messages.error(request, 'Por favor corrigir os erros abaixo.')
#         return render(request=request,
#                       template_name=self.current_step.template_name,
#                       context=self.current_step.get_step_context_data(
#                           event=self.event, form=current_form))
#
#     def pre_flight(self, request):
#
#         slug = self.kwargs.get('slug')
#
#         if not slug:
#             return redirect('https://congressy.com')
#
#         self.event = get_object_or_404(Event, slug=slug)
#
#         if not request.user.is_authenticated:
#             return redirect('public:hotsite', slug=self.event.slug)
#
#         enabled = self.subscription_enabled()
#
#         if not enabled:
#             return redirect('public:hotsite', slug=self.event.slug)
#
#         return None
