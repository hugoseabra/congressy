"""
    Model representation of the Partner Contract entity in the Database
"""
from django.db import models

from gatheros_event.models import Event
from partner.models import Partner, PartnerPlan


class PartnerContract(models.Model):
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='contracts',
    )

    partner_plan = models.ForeignKey(
        PartnerPlan,
        on_delete=models.CASCADE,
        related_name='contracts',
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='partner_contracts',
    )

    def __str__(self):
        return '{}'.format(self.partner_plan.name)

    class Meta:
        verbose_name = 'Contrato de Parceiro'
        verbose_name_plural = 'Contratos de Parceiros'
        unique_together = (
            ("partner", "event"),
        )
