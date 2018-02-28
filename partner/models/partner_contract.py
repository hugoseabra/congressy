"""
    Model representation of the Partner Contract entity in the Database
"""
from django.db import models
from partner.models import Partner, PartnerPlan
from gatheros_event.models import Event


class PartnerContract(models.Model):
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='partner_contracts',
    )

    partner_plan = models.ForeignKey(
        PartnerPlan,
        on_delete=models.CASCADE,
        related_name='partner_contracts',
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='partner_contracts',
    )

    def __str__(self):
        return '{} -- {} - {}'.format(self.event.name,
                                      self.partner.person.name,
                                      self.partner_plan.name)

    class Meta:
        verbose_name = 'Contrato de Parceiro'
        verbose_name_plural = 'Contratos de Parceiros'
