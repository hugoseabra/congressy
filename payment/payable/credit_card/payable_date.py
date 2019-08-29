import calendar
from datetime import date, timedelta
from typing import List

from payment.holidays import brazilian_holidays


class CreditCardPayableDate:
    """
    Calcula datas de pagamento de recebíveis a partir de uma referênia de
    data de transação e quantidade de parcelas.
    """

    # Quantidade de dias para o pagamento da primeira parcela.
    FIRST_PAYMENT_DAYS = 29

    # Intervalo de dias entre pagamentos
    PAYMENT_INTERVAL_DAYS = 30

    def __init__(self, transaction_date: date):
        """
        :param transaction_date: data da transação
        """
        self.transaction_date = transaction_date

        self.holidays = self.get_brasilian_holidays()

    def get_antecipation_date(self, elapsed_days=None) -> date:
        """
        Resgata data de antecipação a partir da data de transação.

        :param elapsed_days: Dias corridos
        :return: Data de antecipação
        """
        if elapsed_days is None:
            elapsed_days = self.FIRST_PAYMENT_DAYS

        antec_date = self.transaction_date + timedelta(days=elapsed_days)

        while True:
            if self.is_business_day(antec_date) is False:
                antec_date = self.get_next_business_day(antec_date)
                continue

            return antec_date

    def get_dates(self, additional_business_days=None) -> List[date]:
        """
        Resgata datas de recebíveis.

        :param additional_business_days: Dias úteis adicionados ao intervalo
            de dias padrão.
        :return:
        """
        first_payment = self.transaction_date + timedelta(
            days=self.FIRST_PAYMENT_DAYS
        )

        if additional_business_days and additional_business_days > 0:
            for additional_day in range(additional_business_days):
                # 2 diais úteis úteis
                first_payment = self.get_next_business_day(first_payment)

        if self.is_business_day(first_payment) is False:
            first_payment = self.get_next_business_day(first_payment)

        date_list = [first_payment]

        for interval in range(1, 12):
            interval_days = interval * self.PAYMENT_INTERVAL_DAYS
            interval_days += self.FIRST_PAYMENT_DAYS
            interval_date = \
                self.transaction_date + timedelta(days=interval_days)

            if additional_business_days and additional_business_days > 0:
                for additional_day in range(additional_business_days):
                    # 2 diais úteis úteis
                    interval_date = self.get_next_business_day(interval_date)

            if self.is_business_day(interval_date) is False:
                interval_date = self.get_next_business_day(interval_date)

            date_list.append(interval_date)

        return date_list

    def get_date(self, installment: int, additional_business_days=None):
        """
        Resgata data de recebível a partir da parcela informada.

        :param installment: Número da parcela
        :param additional_business_days: Dias úteis adicionados ao intervalo
            de dias padrão.
        :return:
        """
        if installment < 1:
            installment = 1

        dates = self.get_dates(additional_business_days)

        if installment > len(dates):
            raise Exception(
                'Quantidade de parcelas ultrapassa a quantidade de datas'
                ' possíveis'
            )

        # -1 por causa do index
        return dates[installment - 1]

    def get_next_business_day(self, ref_date: date) -> date:
        """
        Resgata próximo dia útil, verificando se próximo dia, a partir da data
        de referência, se não é dia é fim de semana (sábado ou domingo)
        e se não está dentre os feriados.

        :param ref_date: data de referência para resgatar o próximo dia útil
        :return: dia útil
        """

        probable_date = ref_date

        while True:
            next_day = probable_date + timedelta(days=1)

            if self.is_business_day(next_day) is False:
                probable_date = next_day
                continue

            return next_day

    def is_business_day(self, ref_date: date) -> bool:
        """
        Verifica se data informada é dia útil

        :param ref_date: Data de referência
        :return: TRUE se dia útil.
        """
        week_day = calendar.day_name[ref_date.weekday()]
        is_weekend = week_day.lower() in ('saturday', 'sunday')
        is_holiday = ref_date in self.holidays

        return is_weekend is False and is_holiday is False

    @staticmethod
    def get_brasilian_holidays():
        return [d[0] for d in brazilian_holidays]
