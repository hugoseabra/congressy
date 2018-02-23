
class PriceCalculator:
    """

    """
    def __init__(self, absorb_transaction_tax=False, absorb_installment_tax=True, installment_taxes=[]):
        """

        :param absorb_transaction_tax: boolean - Flag used to indicate if the responsible for the final price will pay
                                                 the transaction taxes.
                                                 True = Event Owner pays tax.
                                                 False = Congressy pays the taxes.
        :param absorb_installment_tax: boolean - Flag used to indicate if the responsible for the final price will pay
                                                 the installment taxes.
                                                 True = Subscription Owner pays tax.
                                                 False = Event Owner pays the taxes.
        :param installment_taxes: list - A list of taxes used during installments
        """
        self.absorb_transaction_tax = absorb_transaction_tax
        self.installment_taxes = installment_taxes
        self.absorb_installment_tax = absorb_installment_tax


