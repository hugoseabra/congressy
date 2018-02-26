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
        related_name='partner_contract',
    )

    partner_plan = models.ForeignKey(
        PartnerPlan,
        on_delete=models.CASCADE,
        related_name='partner_contract',
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='partner_contract',
    )


