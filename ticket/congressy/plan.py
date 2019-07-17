from decimal import Decimal
from django.conf import settings

from .installment import CongressyInstallment


class CongressyPlan:
    """
    Classe que centraliza fonte de verdade para cálculos de percentual
    da Congressy.
    """
    minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)

    def __init__(self, amount: Decimal, percent: Decimal) -> None:
        self.amount = amount
        self.percent = percent

    def get_congressy_amount(self, ignore_minumum=False) -> Decimal:
        """ Resgata montante destinado à Congressy. """
        congressy_amount = self.amount * self.percent

        if ignore_minumum is False and congressy_amount < self.minimum:
            congressy_amount = self.minimum

        return congressy_amount

    def get_organizer_amount(self) -> Decimal:
        """ Resgata montante destinado ao organizador de evento. """
        return self.amount - self.get_congressy_amount()

    def get_installment(self,
                        num_parts: int,
                        free_parts: int = 1) -> CongressyInstallment:
        """ Resgata calculadora de parcelamento de inscrição. """
        return CongressyInstallment(amount=self.amount,
                                    num_parts=num_parts,
                                    free_parts=free_parts)

    def get_subscriber_price(self, transfer_tax=False):
        """ Resgata valor final a ser pago pelo participante. """

        if transfer_tax is False:
            return self.amount

        return self.amount + self.get_congressy_amount()
