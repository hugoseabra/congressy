from base import managers
from installment.models import Part


class PartManager(managers.Manager):
    class Meta:
        model = Part
        fields = '__all__'
        exclude = [
            'paid',
        ]

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            return amount

        return round(amount, 2)
