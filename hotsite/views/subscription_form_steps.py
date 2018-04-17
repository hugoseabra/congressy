from base.step import Step
from hotsite.forms import LotsForm, SubscriptionPersonForm, SubscriptionForm
from hotsite.views.subscription_form_bootstrappers import LotBootstrapper, \
    PersonBootstrapper


class StepOne(Step):
    template_name = 'hotsite/lot_form.html'
    form_class = LotsForm

    @staticmethod
    def get_step_context_data(event, form=None):
        context = {}

        context['event'] = event

        if not form:
            context['form'] = LotsForm(event=event)

        context['remove_preloader'] = True
        return context


class StepTwo(Step):
    template_name = 'hotsite/person_form.html'
    form_class = SubscriptionPersonForm
    _dependes_on = ('lot',)
    _dependency_bootstrap_map = {'lot': LotBootstrapper}

    def get_step_context_data(self, event, extra_data, **kwargs):

        lot = self.dependency_artifacts['lot']

        context = {}

        coupon_code = extra_data.cleaned_data.get('coupon_code')

        context['event'] = event
        context['form'] = SubscriptionPersonForm(event=event, lot=lot,
                                                 coupon_code=coupon_code)

        if lot.price and lot.price > 0:
            context['has_payments'] = True
        else:
            context['has_payments'] = False

        if lot.event_survey:
            context['has_surveys'] = True
        else:
            context['has_surveys'] = False

        context['remove_preloader'] = True

        return context


class StepFive(Step):
    template_name = 'hotsite/person_form.html'
    form_class = SubscriptionForm
    _dependes_on = ('lot', 'person')
    _dependency_bootstrap_map = {'lot': LotBootstrapper,
                                 'person': PersonBootstrapper}

    def get_step_context_data(self, event, form=None):

        lot = self.dependency_artifacts['lot']

        context = {}

        context['event'] = event

        if not form:
            context['form'] = SubscriptionPersonForm(event=event,
                                                     lot=lot)

        if lot.price and lot.price > 0:
            context['has_payments'] = True
        else:
            context['has_payments'] = False

        if lot.event_survey:
            context['has_surveys'] = True
        else:
            context['has_surveys'] = False

        context['remove_preloader'] = True

        return context


# class StepThree(Step):
#     template = 'hotsite/survey_form.html'
#
#     def __init__(self, request, event, lot, form=None, context=None,
#                  dependency_artifacts=None, **kwargs) -> None:
#         self.event = event
#         self.lot = lot
#
#         super().__init__(request, form, context, dependency_artifacts,
#                          **kwargs)
#
#     def get_context(self):
#         context = super().get_context()
#
#         if not self.form_instance:
#             self.form_instance = LotsForm(event=self.event,
#                                           initial={'next_step': 1})
#
#         context['form'] = self.form_instance
#         context['event'] = self.event
#         context['has_payments'] = False
#         context['remove_preloader'] = True
#
#         if self.lot.price > 0:
#             context['has_payments'] = True
#
#         return context
#
#
# class StepFour(Step):
#     template = 'hotsite/payment_form.html'
#     dependes_on = ('person', 'lot')
#     dependency_bootstrap_map = {'person': PersonBootstrapper,
#                                 'lot': LotBootstrapper}
#
#     def __init__(self, request, event, form=None, context=None,
#                  dependency_artifacts=None, **kwargs) -> None:
#
#         self.event = event
#
#         if form:
#             self.form_instance = form
#
#         super().__init__(request, form, context, dependency_artifacts,
#                          **kwargs)
#
#     def get_context(self):
#
#         person = self.dependency_artifacts['person']
#         lot = self.dependency_artifacts['lot']
#
#         context = super().get_context()
#         lot_obj_as_json = serializers.serialize('json', [lot, ])
#
#         json_obj = json.loads(lot_obj_as_json)
#         json_obj = json_obj[0]
#         json_obj = json_obj['fields']
#
#         del json_obj['exhibition_code']
#         del json_obj['private']
#
#         lot_obj_as_json = json.dumps(json_obj)
#
#         context['lot'] = lot_obj_as_json
#         context['lot_id'] = lot.pk
#         context['person'] = person
#         context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY
#         context['remove_preloader'] = True
#
#         if not self.form_instance:
#             self.form_instance = PaymentForm(
#                 initial={
#                     'next_step': 4,
#                     'previous_step': 3,
#                     'lot': lot.pk,
#                     'person': person.pk
#                 })
#
#         context['form'] = self.form_instance
#         context['event'] = self.event
#
#         return context
#
#
# class StepFive(Step):
#     dependes_on = ('person', 'lot')
#
#     dependency_bootstrap_map = {'person': PersonBootstrapper,
#                                 'lot': LotBootstrapper}
#
#     def __init__(self, request, event, form=None, context=None,
#                  dependency_artifacts=None, **kwargs) -> None:
#         self.event = event
#
#         if self.dependency_artifacts and self.dependency_artifacts['lot']:
#             lot = self.dependency_artifacts['lot']
#
#             if lot.price > 0:
#                 self.dependes_on = ('person', 'lot', 'subscription')
#                 self.dependency_bootstrap_map[
#                     'subscription'] = SubscriptionBootstrapper
#
#         if form:
#             self.form_instance = form
#
#         super().__init__(request, form, context, dependency_artifacts,
#                          **kwargs)
#
#         messages.success(
#             self.request,
#             'Inscrição realizada com sucesso!'
#         )
#
#         subscription = self.dependency_artifacts['subscription']
#
#         if subscription.lot.price is not None and subscription.lot.price > 0:
#             self.redirect_to = reverse_lazy(
#                 'public:hotsite-subscription-status', kwargs={
#                     'slug': self.event.slug})
#
#         else:
#             self.redirect_to = reverse_lazy('public:hotsite',
#                                             kwargs={'slug': self.event.slug})
#
#     def get_context(self):
#
#         context = super().get_context()
#
#         lot = self.dependency_artifacts['lot']
#         person = self.dependency_artifacts['person']
#
#         if not self.form_instance:
#
#             previous_step = 2
#
#             if lot.event_survey:
#                 previous_step = 3
#
#             if lot.price > 0:
#                 previous_step = 4
#
#             self.form_instance = SubscriptionForm(
#                 lot=lot,
#                 initial={
#                     'previous_step': previous_step},
#                 event=self.event,
#                 data=self.request.POST
#             )
#
#         context['form'] = self.form_instance
#
#         try:
#             config = lot.event.formconfig
#         except AttributeError:
#             config = FormConfig()
#
#         if lot.price > 0:
#             config.email = True
#             config.phone = True
#             config.city = True
#
#             config.cpf = config.CPF_REQUIRED
#             config.birth_date = config.BIRTH_DATE_REQUIRED
#             config.address = config.ADDRESS_SHOW
#
#         context['config'] = config
#         context['has_lots'] = lot.event.lots.count() > 1
#
#         return context
