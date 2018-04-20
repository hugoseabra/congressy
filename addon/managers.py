from base import managers
from .models import Price, Theme, OptionalProduct, OptionalService, \
    SubscriptionOptionalService, SubscriptionOptionalProduct


class PriceManager(managers.Manager):
    """ Manager de preços. """

    class Meta:
        model = Price
        fields = '__all__'


class ThemeManager(managers.Manager):
    """ Manager de themas. """

    class Meta:
        model = Theme
        fields = '__all__'


class OptionalProductManager(managers.Manager):
    """ Manager de produtos opcionais. """

    class Meta:
        model = OptionalProduct
        fields = '__all__'


class OptionalServiceManager(managers.Manager):
    """ Manager de serviços opcionais """

    class Meta:
        model = OptionalService
        fields = '__all__'


class SubscriptionOptionalServiceManager(managers.Manager):
    """ Manager de serviços opcionais de inscrições"""

    class Meta:
        model = SubscriptionOptionalService
        fields = '__all__'


class SubscriptionOptionalProducteManager(managers.Manager):
    """ Manager de produtos opcionais de inscrições """

    class Meta:
        model = SubscriptionOptionalProduct
        fields = '__all__'
