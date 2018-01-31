# pylint: disable=W5101
"""
Inscrições de pessoas em eventos conforme registrado no pagarme.
"""

from django.db import models


class Transaction(models.Model):

    # ID da transação.
    id = models.IntegerField(
        primary_key=True,
        unique=True,
    )

    # A qual evento o postback se refere.
    # No caso de transações: transaction_status_changed.
    # Já para subscriptions: subscription_status_changed.
    event = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Status anterior da transação.
    old_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Status ideal para objetos deste tipo, em um fluxo normal, onde autorização e captura são feitos com sucesso,
    # por exemplo.
    desired_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Status para o qual efetivamente mudou.
    current_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Qual o tipo do objeto referido.
    # No caso de transações o valor é 'transaction'.
    # No caso de assinaturas, o valor é 'subscription'
    type_of_object = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Possui todas as informações do objeto.
    # Para acessar objetos internos basta acessar a chave transaction[objeto1][objeto2].
    # Ex: para acessar o ddd: transaction[phone][ddd]
    transaction = models.TextField(
        blank=True,
        null=True,
    )

