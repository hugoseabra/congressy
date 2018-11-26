from base import managers
from installment.models import Contract


class ContractManager(managers.Manager):

    class Meta:
        model = Contract
        fields = '__all__'
        exclude = [
            'limit_date',
            'minimum_amount',
            'liquid_amount',
        ]

    def clean_status(self):
        status = self.cleaned_data.get('status', Contract.OPEN_STATUS)
        if not status:
            status = Contract.OPEN_STATUS

        return status
