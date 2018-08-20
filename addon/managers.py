import base64
import binascii
from uuid import uuid4

from django import forms
from django.core.files.base import ContentFile

from base import managers
from core.forms.widgets import PriceInput, SplitDateTimeBootsrapWidget
from .constants import MINIMUM_RELEASE_DAYS
from .models import (
    Product,
    Service,
    OptionalProductType,
    OptionalServiceType,
    SubscriptionService,
    SubscriptionProduct,
    Theme,
)


class ThemeManager(managers.Manager):
    """ Manager de themas. """

    class Meta:
        model = Theme
        fields = '__all__'


class OptionalProductTypeManager(managers.Manager):
    """ Manager de tipos de opcionais """

    class Meta:
        model = OptionalProductType
        fields = '__all__'


class OptionalServiceTypeManager(managers.Manager):
    """ Manager de tipos de opcionais """

    class Meta:
        model = OptionalServiceType
        fields = '__all__'


class ProductManager(managers.Manager):
    """ Manager de produtos opcionais. """

    banner = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'liquid_price': PriceInput,
            'date_end_sub': SplitDateTimeBootsrapWidget,
        }

    def __init__(self, **kwargs):
        initial = kwargs.get('initial', {})
        if not kwargs.get('instance') and initial.get('release_days') is None:
            initial.update({'release_days': MINIMUM_RELEASE_DAYS})
            kwargs.update({'initial': initial})

        super().__init__(**kwargs)

        if not self.instance.pk or self.instance.liquid_price == 0:
            self.fields['liquid_price'].initial = '0.00'

    def clean_liquid_price(self):
        liquid_price = self.cleaned_data.get('liquid_price')

        # Não é permitido editar preço para opcionais com inscrições.
        if self.instance.pk \
                and self.instance.has_changed('liquid_price') \
                and self.instance.subscription_products \
                        .filter(subscription__completed=True,
                                subscription__test_subscription=False) \
                        .count() > 0:
            raise forms.ValidationError(
                'Este opcional já possui inscrições. Seu valor não pode ser'
                ' alterado.'
            )

        return liquid_price

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')

        if not banner:
            return banner

        # Decoding from base64 avatar into a file obj.
        try:
            file_ext, imgstr = banner.split(';base64,')
            ext = file_ext.split('/')[-1]
            file_name = str(uuid4()) + "." + ext
            banner = ContentFile(
                base64.b64decode(imgstr),
                name=file_name
            )

        except (binascii.Error, ValueError):
            pass

        return banner


class ServiceManager(managers.Manager):
    """ Manager de serviços opcionais """

    banner = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            # 'theme': ManageableSelect,
            'liquid_price': PriceInput,
            'date_end_sub': SplitDateTimeBootsrapWidget,
            'schedule_start': SplitDateTimeBootsrapWidget,
            'schedule_end': SplitDateTimeBootsrapWidget,
        }

    def __init__(self, **kwargs):
        initial = kwargs.get('initial', {})
        if not kwargs.get('instance') and initial.get('release_days') is None:
            initial.update({'release_days': MINIMUM_RELEASE_DAYS})
            kwargs.update({'initial': initial})

        super().__init__(**kwargs)

        if not self.instance.pk or self.instance.liquid_price == 0:
            self.fields['liquid_price'].initial = '0.00'

    def clean_price(self):
        liquid_price = self.cleaned_data.get('liquid_price')

        # Não é permitido editar preço para opcionais com inscrições.
        if self.instance.pk \
                and self.instance.has_changed('liquid_price') \
                and self.instance.subscription_services.filter(
                    subscription__completed=True,
                    subscription__test_subscription=False
                ).count() > 0:
            raise forms.ValidationError(
                'Este opcional já possui inscrições. Seu valor não pode ser'
                ' alterado.'
            )

        return liquid_price

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')

        if not banner:
            return banner

        # Decoding from base64 avatar into a file obj.
        try:
            file_ext, imgstr = banner.split(';base64,')
            ext = file_ext.split('/')[-1]
            file_name = str(uuid4()) + "." + ext
            banner = ContentFile(
                base64.b64decode(imgstr),
                name=file_name
            )

        except (binascii.Error, ValueError):
            pass

        return banner


class SubscriptionServiceManager(managers.Manager):
    """ Manager de serviços opcionais de inscrições"""

    class Meta:
        model = SubscriptionService
        fields = '__all__'

    def clean(self):
        """

        Regra #1: Se quantidade de inscrições já foi atingida,
            novas inscrições não poderão ser realizadas

        Regra #2: Validar restrição de sessão se há restrição por Sessão,
            ou seja, se há outro Optional dentro do mesmo intervalo de
            data e hora final e inicial do Optional informado.

        Regra #3: Validar restrição por tema (LimitByTheme), se há
            restrição por Tema, ou seja, se o Participante já possui X
            opcionais no mesmo tema e não pode mais se cadastrar em outro.

        Regra #4:
            Deve restringir a criação de inscrições em opcionais caso o
            opcional selecionado esteja com a data/hora final antes da
            data/hora atual.

        """
        cleaned_data = super().clean()

        optional_service = cleaned_data['optional']
        subscription = cleaned_data['subscription']

        # Regra 1
        if optional_service.has_quantity_conflict:
            raise forms.ValidationError(
                'Quantidade de inscrições já foi atingida, '
                'novas inscrições não poderão ser realizadas')

        # Regra 2:
        if optional_service.has_schedule_conflicts:
            conflicting_service = \
                optional_service.get_schedule_conflict_service
            raise forms.ValidationError(
                'Conflito de horário - o opcional "{}" '
                'está em conflito com o opcional "{}".'.format(
                    optional_service.name,
                    conflicting_service.name
                )
            )

        # Regra 3:
        if optional_service.theme.limit:

            total = 0

            for optional in subscription.subscription_services.all():

                if optional.optional.theme == optional_service.theme:
                    total += 1

            if total >= optional_service.theme.limit:
                raise forms.ValidationError(
                    'Limite por tema excedido: limite do ''tema {} já foi '
                    'atingido'.format(optional_service.theme.name)
                )

        # Regra 4
        if optional_service.has_sub_end_date_conflict:
            raise forms.ValidationError(
                'Este opcional já expirou e não aceita mais inscrições.'
            )

        return cleaned_data


class SubscriptionProductManager(managers.Manager):
    """ Manager de produtos opcionais de inscrições """

    class Meta:
        model = SubscriptionProduct
        fields = '__all__'

    def clean(self):
        """
        Regra #1:
            Se quantidade de inscrições já foi atingida, novas inscrições
            não poderão ser realizadas

        Regra #2:
            Deve restringir a criação de inscrições em opcionais caso o
            opcional selecionado esteja com a data/hora final antes da
            data/hora atual.

        """
        cleaned_data = super().clean()

        product = cleaned_data['optional']

        # Regra 1
        if product.has_quantity_conflict:
            raise forms.ValidationError(
                'Quantidade de inscrições já foi atingida, '
                'novas inscrições não poderão ser realizadas')

        # Regra 2
        if product.has_sub_end_date_conflict:
            raise forms.ValidationError(
                'Este opcional já expirou e não aceita mais inscrições.'
            )

        return cleaned_data
