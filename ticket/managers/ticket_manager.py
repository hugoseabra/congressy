from django.core.exceptions import ValidationError

from base.managers import Manager
from ticket.models import Ticket


class TicketManager(Manager):
    class Meta:
        model = Ticket
        fields = '__all__'

    def clean_free_installments(self):
        free_installments = self.cleaned_data['free_installments']
        if free_installments and free_installments > 10:
            raise ValidationError('é possivel absorver no máximo 10 parcelas')

        return free_installments
