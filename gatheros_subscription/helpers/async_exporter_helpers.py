import logging
import os
from pathlib import Path

from django.conf import settings

from gatheros_event.models import Event

logger = logging.getLogger(__name__)


def has_export_lock(event: Event) -> bool:
    lock_file_path = _get_lock_file_path(event)

    return os.path.exists(lock_file_path)


def create_export_lock(event: Event) -> None:
    lock_file_path = _get_lock_file_path(event)
    exporter_folder_path = _get_exporter_folder_path(event)

    if not os.path.isdir(exporter_folder_path):
        logger.info("Creating exporter lock folder for event id: {}".format(
            event.pk
        ))
        os.makedirs(exporter_folder_path)

    if os.path.exists(lock_file_path):
        logger.warning("Attempt to create a lock of existing lock on "
                       "event id: {}".format(event.pk))
        return

    logger.info("Creating lock file for event id: {}".format(event.pk))
    Path(lock_file_path).touch()


def remove_export_lock(event: Event) -> None:
    lock_file_path = _get_lock_file_path(event)

    if not os.path.exists(lock_file_path):
        logger.warning("Attempt to remove a lock of inexistent lock on "
                       "event id: {}".format(event.pk))
        return
    logger.info("Removing lock file for event id: {}".format(event.pk))
    os.remove(lock_file_path)


def has_existing_export_files(event: Event) -> bool:
    exporter_folder_path = _get_exporter_folder_path(event)

    if not os.path.isdir(exporter_folder_path):
        return False

    for file in os.listdir(exporter_folder_path):
        if file.endswith(".xlsx"):
            return True

    return False


def create_export_file(event: Event, payload: bytes) -> None:
    exporter_folder_path = _get_exporter_folder_path(event)
    exporter_file_path = exporter_folder_path + 'cgsy.xlsx'

    if not os.path.isdir(exporter_folder_path):
        logger.info("Creating exporter lock folder for event id: {}".format(
            event.pk
        ))
        os.makedirs(exporter_folder_path)

    f = open(exporter_file_path, 'wb')
    f.write(payload)
    f.close()
    logger.info(
        "Created export file '{}' for event id: {}".format(
            exporter_file_path,
            event.pk,
        )
    )


def remove_export_files(event: Event) -> None:
    exporter_folder_path = _get_exporter_folder_path(event)

    for file in os.listdir(exporter_folder_path):
        if file.endswith(".xlsx"):
            logger.info("Removing export file '{}' for event id: {}".format(
                file,
                event.pk
            ))
            os.remove(exporter_folder_path + file)


def get_export_file_path(event: Event) -> str:
    return _get_exporter_folder_path(event) + 'cgsy.xlsx'


def _get_lock_file_path(event: Event) -> str:
    return _get_exporter_folder_path(event) + 'cgsy.lock'


def _get_exporter_folder_path(event: Event) -> str:
    media_url = settings.MEDIA_ROOT
    exporter_url = '/subscription_exporter/'
    return media_url + exporter_url + '{}/'.format(event.pk)
