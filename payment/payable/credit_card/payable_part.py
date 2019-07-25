"""
Primeiramente o valor, em centavos, é dividido pelo número de parcelas.
Vamos denominar constantes:
x=valor
y=número de parcelas
z=x/y  , sem as casas decimais e sem arredondamento ( exemplo: z=5/3=1 )

Após isso é calculado o módulo de x e y.
a=(x%y)
Se a <=1
Primeira parcela -> a+ z
Demais parcelas -> z
Se a > 1
Calcular o módulo de a pelo número de parcelas – 1, que é o valor a ser usado na primeira parcela.
b=a%(y-1)
Se b≤(y-1), b passa a ser igual a:
b=(y-1-b)
Calcular o valor a ser usado nas demais parcelas.
c=((b+a))/((y-1))
As parcelas ficarão iguais a:
Primeira parcela =z+[(-1)×a]
Demais parcelas =z+c

"""

from decimal import Decimal
from typing import List


def get_part_amounts(amount: Decimal, installments=1) -> List[Decimal]:
    """
    Resgata lista de valores de parcelas de um montante
    :param amount: Montante total
    :param installments: Número de parcelas
    :return: Lista de parcelas
    """
    if installments <= 1:
        installments = 1

    if installments == 1:
        return [amount]

    amounts = list()

    # PAGAR.ME Formula de parcelas

    # valor em centavos
    x = int(round(amount, 2) * 100)
    y = installments
    z = int(x / y)

    a = x % y

    if a <= 1:
        total = z * (y - 1)
        first = x - total

        amounts.append(Decimal(first / 100))

        for part in range(1, y):
            amounts.append(Decimal(z / 100))

    else:
        b = a % (y - 1)

        if b <= y - 1:
            b = y - 1 - b

        c = int((b + a) / (y - 1))

        part_amount = z + c

        total = part_amount * (y - 1)
        first = x - total

        amounts.append(Decimal(first / 100))

        for part in range(1, y):
            amounts.append(Decimal(part_amount / 100))

    total = round(sum(amounts), 2)

    assert total == round(amount, 2), \
        'Erro no cálculo de parcelas - parcelas: {}, montante: {}'.format(
            total,
            round(amount, 2)
        )

    return amounts
