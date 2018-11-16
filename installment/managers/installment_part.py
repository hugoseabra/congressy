from base import managers
from installment.models import InstallmentPart


class InstallmentPartManager(managers.Manager):
    class Meta:
        model = InstallmentPart
        fields = '__all__'
