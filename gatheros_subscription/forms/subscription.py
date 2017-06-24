import json

from django import forms
from kanu_locations.models import City

from .event_form import EventConfigForm


class SubscriptionForm(EventConfigForm):
    def __init__(self, instance=None, hide_lot=True, *args, **kwargs):
        self.instance = instance
        super(SubscriptionForm, self).__init__(*args, **kwargs)
        self._adjust_initial_data()

        self._add_lot_field(hide_lot)

    def _adjust_initial_data(self):
        """ Ajusta valores iniciais de acordo com os campos."""

        if not self.instance:
            return

        for field_name in self.gatheros_fields:
            field = self.get_gatheros_field_by_name(field_name)
            if not field:
                continue

            answer = field.answer(subscription=self.instance)
            if not answer:
                continue

            if isinstance(answer, City):
                answer = answer.pk

            elif not field.form_default_field:
                try:
                    answer = json.loads(answer.value)
                except ValueError:
                    continue

                if isinstance(answer, dict):
                    answer = answer['value']

            answer = answer.strip() if isinstance(answer, str) else answer
            self.initial.update({field_name: answer})

    def _add_lot_field(self, hide_lot=True):

        choices = [('', '- Selecione -')]
        lots = self.form.event.lots.all().order_by('name')
        [choices.append((lot.pk, lot.name,)) for lot in lots]

        lot = forms.ChoiceField(
            label='Lote',
            required=True,
            choices=choices,
            initial=self.instance.lot.pk if self.instance else None
        )

        event = self.form.event

        # Event com inscrição que não seja por lote deve esconder o campo
        if event.subscription_type != event.SUBSCRIPTION_BY_LOTS or hide_lot:
            lot.widget = forms.HiddenInput()

        self.fields['lot'] = lot
