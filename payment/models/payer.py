from django.db import models

from base.models import EntityMixin
from base.models import RuleChecker, RuleIntegrityError


class BeneficiarySameSubscriptionPerson(RuleChecker):
    """
    Regra: A pessoa da inscrição é a mesma beneficiária do pagador.
    """

    def check(self, model_instance, *args, **kwargs):
        sub_person_pk = model_instance.subscription.person_id
        beneficiary_person_pk = model_instance.benefactor.beneficiary_id

        if sub_person_pk != beneficiary_person_pk:
            raise RuleIntegrityError(
                'O benfeitor (pagador) e a pessoa da inscrição são diferentes.'
            )


class TransactionSameSubscription(RuleChecker):
    """
    Regra: A pessoa da inscrição é a mesma beneficária do pagador.
    """

    def check(self, model_instance, *args, **kwargs):
        sub_pk = model_instance.subscription_id
        trans_sub_pk = model_instance.transaction.subscription_id

        if sub_pk != trans_sub_pk:
            raise RuleIntegrityError(
                'A transação não pertence à inscrição do pagador.'
            )


class Payer(EntityMixin, models.Model):
    class Meta:
        verbose_name = 'pagador de inscrição'
        verbose_name_plural = 'pagadores de inscrição'
        unique_together = (
            ('benefactor', 'subscription', 'transaction',)
        )

    rule_instances = (
        BeneficiarySameSubscriptionPerson,
        TransactionSameSubscription,
    )

    transaction = models.OneToOneField(
        'payment.Transaction',
        on_delete=models.CASCADE,
        verbose_name='transaction',
        related_name='payer',
        null=False,
        blank=False,
    )

    subscription = models.ForeignKey(
        'gatheros_subscription.Subscription',
        on_delete=models.CASCADE,
        verbose_name='inscrição',
        related_name='payers',
        null=False,
        blank=False,
    )

    lot = models.ForeignKey(
        'gatheros_subscription.Lot',
        on_delete=models.PROTECT,
        verbose_name='lote',
        related_name='payers',
        # Making field write once
        editable=False,
        null=False,
    )

    benefactor = models.ForeignKey(
        'payment.Benefactor',
        on_delete=models.CASCADE,
        verbose_name='benfeitor',
        related_name='payers',
        null=False,
        blank=False,
    )

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.lot_id = self.subscription.lot_id
        super().save(*args, **kwargs)
