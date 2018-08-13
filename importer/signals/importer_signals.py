""" Signals do model `CSVFileConfig`. """
import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from importer.models import CSVFileConfig


@receiver(pre_delete, sender=CSVFileConfig)
def clear_files_on_delete(instance, **_):
    """ Apaga arquivos relacionados quando CSVFileConfig é apagado """

    path = None

    def _delete_media(field):
        """ Lógica de remoção de arquivos """
        nonlocal path
        if bool(field) and os.path.isfile(field.path):
            path = os.path.dirname(field.path)
            field.delete(False)

    # Chamando remoção de arquivos
    _delete_media(instance.csv_file)
    _delete_media(instance.error_csv_file)
    _delete_media(instance.correction_csv_file)

    # Remove diretório se estiver vazio
    if path and not os.listdir(path):
        os.rmdir(path)
