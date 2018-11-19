from base import managers
from installment.models import InstallmentContract


class InstallmentContractManager(managers.Manager):

    class Meta:
        model = InstallmentContract
        fields = '__all__'
        exclude = [
            'status',
            'minimum_amount_creation',
        ]
