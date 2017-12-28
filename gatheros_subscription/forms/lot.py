""" Formulários de `Lot` """
from django import forms

from gatheros_subscription.models import Lot


class LotForm(forms.ModelForm):
    """ Formulário de lote. """
    event = None

    class Meta:
        """ Meta """
        model = Lot
        fields = [
            'event',
            'name',
            'date_start',
            'date_end',
            'limit',
            'price',
            # 'discount_type',
            # 'discount',
            'transfer_tax',
            'private'
        ]
        widgets = {'event': forms.HiddenInput(),
                   'price': forms.TextInput(),
                   }

    def __init__(self, **kwargs):
        super(LotForm, self).__init__(**kwargs)
        self.event = kwargs.get('initial').get('event')
        self._set_dates_help_texts()

    def _set_dates_help_texts(self):
        last_lot = self.event.lots.last()
        if last_lot:
            diff = self.event.date_start - last_lot.date_end

            if diff.days <= 1:
                date_start_help = 'O lote anterior ({}) pega todo o período' \
                                  ' do evento.'.format(last_lot.name)
            else:
                lot_date_end = last_lot.date_end.strftime('%d/%m/%Y %Hh%M')
                date_start_help = \
                    'Existe um lote anterior ({}) que finaliza em {}. Tente' \
                    ' não chocar as datas.'.format(last_lot.name, lot_date_end)

            self.fields['date_start'].help_text = date_start_help

        event_date_start = self.event.date_start.strftime('%d/%m/%Y %Hh%M')
        self.fields['date_end'].help_text = \
            'O evento inicia-se em {}. O final do lote deve ser anterior a' \
            ' esta data.'.format(event_date_start)
