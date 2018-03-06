""" Formulários de `Lot` """
from datetime import timedelta, datetime

from django import forms

from gatheros_subscription.models import Lot


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class DateTimeInput(forms.DateTimeInput):
    input_type = 'tel'


INSTALLMENT_CHOICES = (
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
)


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
            'private',
            'exhibition_code',
            'transfer_tax',
            'allow_installment',
            'installment_limit',
            'num_install_interest_absortion',
        ]

        widgets = {
            'event': forms.HiddenInput(),
            'price': TelephoneInput(),
            'date_start': DateTimeInput(attrs={'placeholder': 'dd/mm/aaaa '
                                                              'hh:mm'}),
            'date_end': DateTimeInput(attrs={'placeholder': 'dd/mm/aaaa '
                                                            'hh:mm'}),
            'installment_limit': forms.Select(
                choices=INSTALLMENT_CHOICES
            ),
            'num_install_interest_absortion': forms.Select(
                choices=((0, 0,),) + INSTALLMENT_CHOICES
            ),
        }

    def __init__(self, lang='pt-br', **kwargs):
        self.lang = lang

        self.event = kwargs.get('initial').get('event')

        super(LotForm, self).__init__(**kwargs)

        if self.instance.pk and self.instance.subscriptions.count() > 0:
            self.fields['price'].widget.attrs['disabled'] = 'disabled'
            self.fields['price'].disabled = True

    def _set_dates_help_texts(self):
        last_lot = self.event.lots.last()

        if not last_lot:
            return

        if self.instance.pk == last_lot.pk:
            date_start_help = \
                'Este lote pega todo o período anterior ao' \
                ' evento.'.format(last_lot.name)

        else:
            diff = self.event.date_start - last_lot.date_end
            if diff.days <= 1:
                date_start_help = \
                    'O lote anterior ({}) pega todo o' \
                    ' período anterior ao evento.'.format(last_lot.name)
            else:
                lot_date_end = last_lot.date_end.strftime('%d/%m/%Y %Hh%M')
                date_start_help = \
                    'Existe um lote anterior ({}) que finaliza em {}.' \
                    ' Tente não chocar as' \
                    ' datas.'.format(last_lot.name, lot_date_end)

        self.fields['date_start'].help_text = date_start_help

        event_date_start = self.event.date_start.strftime('%d/%m/%Y %Hh%M')

        self.fields['date_end'].help_text = \
            'O evento inicia-se em {}. O final do lote será anterior a' \
            ' este data.'.format(event_date_start)

    def clean(self):
        cleaned_data = super().clean()
        raw_data = self.data

        date_start = datetime.strptime(raw_data['date_start'],
                                       '%d/%m/%Y %H:%M')
        cleaned_data['date_start'] = date_start

        if 'date_end' in raw_data and raw_data['date_end']:
            date_end = datetime.strptime(
                raw_data['date_end'],
                '%d/%m/%Y %H:%M'
            )
            cleaned_data['date_end'] = date_end
        else:
            cleaned_data['date_end'] = \
                self.event.date_end - timedelta(minutes=1)

        price = self.cleaned_data.get('price')
        if price is not None and price > 0 and (price < 10 or price > 30000):
            raise forms.ValidationError(
                {
                    'price': 'Você deve informar um valor entre a R$ 10,00'
                             ' e R$ 30.000,00'
                }
            )

        # Não é permitido editar preço para lotes com inscrições.
        if self.instance.pk \
                and self.instance.has_changed('price') \
                and self.instance.subscriptions.count() > 0:
            raise forms.ValidationError(
                {
                    'price': 'Este lote já possui inscrições. Seu valor não'
                             ' pode ser alterado.'
                }
            )

        return cleaned_data
