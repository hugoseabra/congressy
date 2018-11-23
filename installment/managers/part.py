from base import managers
from installment.models import Part


class PartManager(managers.Manager):
    class Meta:
        model = Part
        fields = '__all__'
        exclude = [
            'paid'
        ]

