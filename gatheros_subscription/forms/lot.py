""" Formulários de `Lot` """
from datetime import timedelta, datetime

from django import forms

from gatheros_subscription.models import Lot
from core.forms import SplitDateTimeWidget, TelephoneInput

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
            'date_start': SplitDateTimeWidget(),
            'date_end': SplitDateTimeWidget(),
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

        instance = kwargs.get('instance')
        if not instance or instance and not instance.exhibition_code:
            initial = kwargs.get('initial', {})
            initial.update(
                {'exhibition_code': Lot.objects.generate_promo_code()}
            )
            kwargs['initial'] = initial

        super(LotForm, self).__init__(**kwargs)

        if self.instance.pk and self.instance.subscriptions.count() > 0:
            self.fields['price'].widget.attrs['disabled'] = 'disabled'
            self.fields['price'].disabled = True

    def clean_date_end(self):
        date_end = self.cleaned_data.get('date_end')
        if not date_end:
            date_end = datetime.now() - timedelta(minutes=1)

        date_start = self.cleaned_data.get('date_start')
        if date_start and date_start > date_end:
            raise forms.ValidationError(
                'Data inicial deve ser anterior a data final.'
            )

        return date_end

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price > 0 and (price < 10 or price > 30000):
            raise forms.ValidationError(
                'Você deve informar um valor entre a R$ 10,00 e R$ 30.000,00'
            )

        # Não é permitido editar preço para lotes com inscrições.
        if self.instance.pk \
                and self.instance.has_changed('price') \
                and self.instance.subscriptions.count() > 0:
            raise forms.ValidationError(
                'Este lote já possui inscrições. Seu valor não pode ser'
                ' alterado.'
            )

        return cleaned_data

    def clean_exhibition_code(self):
        code = self.cleaned_data.get('exhibition_code')
        if code:
            code = ''.join(code.split())
        return code
