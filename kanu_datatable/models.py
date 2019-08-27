import os

from django.db import connection, transaction
from django.db.models.signals import pre_migrate
from django.dispatch import receiver


@transaction.atomic
@receiver(pre_migrate)
def setup_postgres_unaccent(sender, **kwargs):
    """
    Função para tentar configurar a extensão do postgres

    :param sender:
    :param kwargs:
    :return:
    """

    " Não tenta novamente após a primeira falha "
    if os.environ.get("unaccent_tried", 'False') == 'True':
        return None

    print("  Tentando instalar extensão 'unaccent'... ", end='')
    os.environ.setdefault("unaccent_tried", 'True')

    try:
        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
        print("\033[0;92;1m OK \033[0m")
    except:
        print("\033[0;33;1m Não foi possível instalar \033[0m")
