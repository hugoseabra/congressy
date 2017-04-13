from random import choice
from string import digits

"""
Código de 6 dígitos + dígito verificador com dois algarismos: 000000-0

000

Um código processando mediante a concatenação das seguintes informações:
1. 1 primeiros dígitos numericos e maiores que zero encontrados no 'PK' de person
2. 3 dígitos numéricos gerados randomicamente
3. A soma final do 'PK' do lote.
"""


def _get_numbers_from_uuid(uuid, size=3):
    digits = ''
    for i, c in enumerate(uuid):
        if len(str(digits)) == size:
            continue

        if c.isnumeric() and int(c) > 0:
            digits += str(c)

    return digits


part1 = _get_numbers_from_uuid(uuid='0ef90d46-c316-4f81-b768-36e3080cecf0', size=2)
part2 = ''.join(choice(digits) for i in range(3))

code = str(part1 + part2)

print(code)

