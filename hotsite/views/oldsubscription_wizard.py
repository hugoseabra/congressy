# from datetime import datetime
#
# from django import forms
# from django.contrib import messages
# from django.core.exceptions import ObjectDoesNotExist
# from django.db import transaction
# from django.http import HttpResponseBadRequest
# from django.shortcuts import redirect
# from django.views import generic
#
# from gatheros_event.models import Event, Person
# from gatheros_subscription.models import Subscription
# from hotsite.forms import LotsForm, SubscriptionPersonForm, SubscriptionForm
# from hotsite.views.mixins import EventMixin
# from hotsite.views.subscription_form_bootstrappers import LotBootstrapper, \
#     EventSurveyBootstrapper, PersonBootstrapper
# from hotsite.views.subscription_form_steps import StepOne, StepTwo, \
#     StepThree, StepFour, StepFive
# from payment.exception import TransactionError
# from payment.helpers import PagarmeTransactionInstanceData
# from payment.tasks import create_pagarme_transaction
# from survey.directors import SurveyDirector
#
# from base.form_wizard import FormWizard
#
#
# class SubscriptionFormIndexView(EventMixin, generic.View):
#     """
#         View responsavel por decidir onde se inicia o process de inscrição
#     """
#
#     def dispatch(self, request, *args, **kwargs):
#         response = super().dispatch(request, *args, **kwargs)
#
#         if not request.user.is_authenticated:
#             return redirect('public:hotsite', slug=self.event.slug)
#
#         enabled = self.subscription_enabled()
#         if not enabled:
#             return redirect('public:hotsite', slug=self.event.slug)
#
#         return response
#
#     def get(self, request, *args, **kwargs):
#
#         """
#             Se for evento com inscrição por lotes, ir para o step 1,
#             caso contrario pode pular direto para o step 2.
#         """
#         if self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS:
#
#             step_1 = StepOne(
#                 request=request,
#                 event=self.event,
#                 context={
#                     'event': self.event,
#                     'remove_preloader': True
#                 })
#
#             return step_1.render()
#
#         elif self.event.subscription_type == Event.SUBSCRIPTION_SIMPLE:
#
#             lot = self.event.lots.first()
#
#             step_2 = StepTwo(request=request, event=self.event,
#                              dependency_artifacts={'lot': lot}, )
#
#             return step_2.render()
#
#     def post(self, request, *args, **kwargs):
#
#         incoming_step = request.POST.get('next_step')
#         previous_step = request.POST.get('previous_step')
#
#         next_step = int(incoming_step)
#         previous_step = int(previous_step)
#
#         if next_step or previous_step:
#             step_to_be_rendered = next_step if next_step else previous_step
#
#             return HttpResponseBadRequest()
#
#     def clear_string(self, field_name):
#
#         if field_name not in self.request.POST:
#             return
#
#         value = self.request.POST.get(field_name)
#
#         if not value:
#             return ''
#
#         value = value \
#             .replace('.', '') \
#             .replace('-', '') \
#             .replace('/', '') \
#             .replace('(', '') \
#             .replace(')', '') \
#             .replace(' ', '')
#
#         self.request.POST[field_name] = value
#
#
# class SubscriptionWizard(FormWizard):
#
#     steps = {
#         1: StepOne,
#         2: StepTwo,
#         3: StepThree,
#         4: StepFour,
#         5: StepFive
#     }
