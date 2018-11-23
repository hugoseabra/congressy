from base import managers
from installment.models import Contract


class ContractManager(managers.Manager):

    class Meta:
        model = Contract
        fields = '__all__'
        exclude = [
            'limit_date',
            'minimum_amount_creation',
            'minimum_amount',
            'liquid_amount',
        ]
