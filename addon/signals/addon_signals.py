""" Signals do model `addons` """
import os
import shutil

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from addon.models import Service, Product
from gatheros_event.signals.helpers import (
    update_event_config_flags,
    update_event_publishing,
)


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Service)
@receiver(pre_delete, sender=Product)
@receiver(pre_delete, sender=Service)
def set_feature_flags_on_event_type_change(instance, **_):
    """ Altera as flags de fatures quando um evento muda de tipo """

    event = instance.lot_category.event
    update_event_config_flags(event)
    update_event_publishing(event)


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Service)
def erase_previous_files(instance, raw, created, **_):
    if raw is True and created is True:
        return

    if instance.has_changed('banner'):
        current_banner_path = instance.banner.path

        # Inclui os arquivos do StdImage
        current_paths = [
            current_banner_path,
            instance.banner.default.path,
            instance.banner.thumbnail.path,
        ]

        base_dir = os.path.dirname(current_banner_path)
        if not os.path.isdir(base_dir):
            return

        for file in os.listdir(base_dir):
            file_path = os.path.join(base_dir, file)

            if file_path in current_paths:
                continue

            if os.path.isfile(file_path):
                os.unlink(file_path)

            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
