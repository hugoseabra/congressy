import json

from django.core import serializers

from base.form_step import Step
from gatheros_subscription.models import FormConfig
from hotsite.forms import LotsForm, SubscriptionPersonForm, PaymentForm
from hotsite.views.subscription_form_bootstrappers import LotBootstrapper, \
    SubscriptionBootstrapper


class StepOne(Step):
    template = 'hotsite/lot_form.html'

    def __init__(self, request, event, form=None, context=None,
                 dependency_artifacts=None, **kwargs) -> None:
        self.event = event

        super().__init__(request, form, context, dependency_artifacts,
                         **kwargs)

    def get_context(self):
        context = super().get_context()

        if not self.form_instance:
            self.form_instance = LotsForm(event=self.event,
                                          initial={'next_step': 1})

        context['form'] = self.form_instance

        return context


class StepTwo(Step):
    dependes_on = ('lot',)
    dependency_bootstrap_map = {'lot': LotBootstrapper}
    template = 'hotsite/person_form.html'

    def __init__(self, request, event, form=None, context=None,
                 dependency_artifacts=None, **kwargs) -> None:

        self.event = event

        lot_pk = None

        if form:
            self.form_instance = form

        super().__init__(request, form, context, dependency_artifacts,
                         event=self.event, lot_pk=lot_pk, **kwargs)

    def get_context(self):

        context = super().get_context()

        lot = self.dependency_artifacts['lot']

        if not self.form_instance:
            self.form_instance = SubscriptionPersonForm(
                lot=lot,
                initial={
                    'next_step': 2,
                    'lot': lot.pk},
                event=self.event
            )

        context['form'] = self.form_instance
        context['event'] = self.event
        context['remove_preloader'] = True

        try:
            config = lot.event.formconfig
        except AttributeError:
            config = FormConfig()

        if lot.price > 0:
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        context['config'] = config
        context['has_lots'] = lot.event.lots.count() > 1

        return context


class StepThree(Step):
    template = 'hotsite/survey_form.html'

    def __init__(self, request, event, form=None, context=None,
                 dependency_artifacts=None, **kwargs) -> None:
        self.event = event

        super().__init__(request, form, context, dependency_artifacts,
                         **kwargs)

    def get_context(self):
        context = super().get_context()

        if not self.form_instance:
            self.form_instance = LotsForm(event=self.event,
                                          initial={'next_step': 1})

        context['form'] = self.form_instance
        context['event'] = self.event

        return context


class StepFour(Step):
    template = 'hotsite/payment_form.html'
    dependes_on = ('subscription',)
    dependency_bootstrap_map = {'subscription': SubscriptionBootstrapper}

    def __init__(self, request, event, form=None, context=None,
                 dependency_artifacts=None, **kwargs) -> None:

        self.event = event

        if form:
            self.form_instance = form

        super().__init__(request, form, context, dependency_artifacts,
                         **kwargs)

    def get_context(self):

        subscription = self.dependency_artifacts['subscription']

        context = super().get_context()
        lot_obj_as_json = serializers.serialize('json', [subscription.lot, ])

        json_obj = json.loads(lot_obj_as_json)
        json_obj = json_obj[0]
        json_obj = json_obj['fields']

        del json_obj['exhibition_code']
        del json_obj['private']

        lot_obj_as_json = json.dumps(json_obj)

        context['lot'] = lot_obj_as_json
        context['person'] = subscription.person

        if not self.form_instance:
            self.form_instance = PaymentForm(
                initial={
                    'next_step': 4,
                })

        context['form'] = self.form_instance
        context['event'] = self.event

        return context


class StepFive(Step):
    template = 'hotsite/lot_form.html'

    def __init__(self, request, event, form=None, context=None,
                 dependency_artifacts=None, **kwargs) -> None:
        self.event = event

        super().__init__(request, form, context, dependency_artifacts,
                         **kwargs)

    def get_context(self):
        context = super().get_context()

        if not self.form_instance:
            self.form_instance = LotsForm(event=self.event,
                                          initial={'next_step': 1})

        context['form'] = self.form_instance

        return context