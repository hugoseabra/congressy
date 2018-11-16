from base import managers
from installment.models import InstallmentContract


class InstallmentContractManager(managers.Manager):
    class Meta:
        model = InstallmentContract
        fields = '__all__'
