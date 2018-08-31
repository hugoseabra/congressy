import os
import shutil

from django.db.models.signals import post_save
from django.dispatch import receiver

from addon.models import Product, Service


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
