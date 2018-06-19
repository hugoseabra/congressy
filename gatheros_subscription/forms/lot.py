""" Formulários de `Lot` """
from datetime import datetime, timedelta

from django import forms
from core.forms.widgets import SplitDateTimeBootsrapWidget
from core.forms import PriceInput
from gatheros_subscription.models import EventSurvey, LotCategory, Lot

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
            'category',
            'name',
            'date_start',
            'date_end',
            # 'limit',
            'price',
            # 'private',
            # 'exhibition_code',
            'transfer_tax',
            'allow_installment',
            'installment_limit',
            'num_install_interest_absortion',
            'rsvp_restrict',
            # 'event_survey',
        ]

        widgets = {
            'event': forms.HiddenInput(),
            'price': PriceInput(),
            'date_start': SplitDateTimeBootsrapWidget(),
            'date_end': SplitDateTimeBootsrapWidget(),
            'installment_limit': forms.Select(
                choices=INSTALLMENT_CHOICES
            ),
            'num_install_interest_absortion': forms.Select(
                choices=((0, 0,),) + INSTALLMENT_CHOICES
            ),
        }

    def __init__(self, **kwargs):
        self.event = kwargs.get('initial').get('event')

        instance = kwargs.get('instance')
        if not instance or instance and not instance.exhibition_code:
            initial = kwargs.get('initial', {})
            initial.update(
                {'exhibition_code': Lot.objects.generate_promo_code()}
            )
            kwargs['initial'] = initial

        super(LotForm, self).__init__(**kwargs)

        initial = kwargs.get('initial')
        event_pk = initial.get('event')

        self.fields['category'] = forms.ModelChoiceField(
            queryset=LotCategory.objects.filter(event_id=event_pk),
            label='Categoria',
        )

        self.fields['event_survey'] = forms.ModelChoiceField(
            queryset=EventSurvey.objects.filter(event=self.event),
            label='Selecione um questionário',
            required=False,
        )
        self.fields['event_survey'].empty_label = '- Selecione -'

        if self.instance.pk and self.instance.subscriptions.filter(
                completed=True
        ).count() > 0:
            self.fields['price'].widget.attrs['disabled'] = 'disabled'
            self.fields['price'].disabled = True

            self.fields['transfer_tax'].widget.attrs['disabled'] = 'disabled'
            self.fields['transfer_tax'].disabled = True

            # self.fields['allow_installment'].widget.attrs['disabled'] = \
            #     'disabled'
            # self.fields['allow_installment'].disabled = True

            self.fields['installment_limit'].widget.attrs['disabled'] = \
                'disabled'
            self.fields['installment_limit'].disabled = True

            self.fields[
                'num_install_interest_absortion'
            ].widget.attrs['disabled'] = 'disabled'
            self.fields['num_install_interest_absortion'].disabled = True

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

        # Se vinculado à opcionais e/ou atividades extras,
        # não permitir alterar valor para "0" (setar como gratuito).
        if self._lot_has_optionals() and price == 0:
            raise forms.ValidationError(
                'Esse lote está em uma categoria que já possui opcionais e não'
                ' pode mais ter preço grátis.'
            )

        return price

    def clean_exhibition_code(self):
        code = self.cleaned_data.get('exhibition_code')
        if code:
            code = ''.join(code.split()).upper()

        queryset = Lot.objects.filter(exhibition_code=code)
        if self.instance.pk is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.count() > 0:
            raise forms.ValidationError('Este código já existe.')

        return code

    def _lot_has_optionals(self):
        lot_category = self.instance.category

        if lot_category is not None:

            products = lot_category.product_optionals.all().count()
            services = lot_category.service_optionals.all().count()

            if services > 0 or products > 0:
                return True

        return False
