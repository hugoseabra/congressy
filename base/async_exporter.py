import logging
import os
from pathlib import Path

from django.conf import settings

from gatheros_event.models import Event


class BaseAsyncExporter:
    exporter_url = None

    def __init__(self, event: Event) -> None:
        self.event = event
        self.logger = logging.getLogger(__name__)
        assert self.exporter_url is not None, "exporter_url cannot be None"

    def has_export_lock(self) -> bool:
        lock_file_path = self._get_lock_file_path()

        return os.path.exists(lock_file_path)

    def create_export_lock(self) -> None:
        lock_file_path = self._get_lock_file_path()
        exporter_folder_path = self._get_exporter_folder_path()

        if not os.path.isdir(exporter_folder_path):
            self.logger.info(
                "Creating exporter lock folder for event id: {}".format(
                    self.event.pk
                ))
            os.makedirs(exporter_folder_path)

        if os.path.exists(lock_file_path):
            self.logger.warning("Attempt to create a lock of existing lock on "
                                "event id: {}".format(self.event.pk))
            return

        self.logger.info(
            "Creating lock file for event id: {}".format(self.event.pk))
        Path(lock_file_path).touch()

    def remove_export_lock(self) -> None:
        lock_file_path = self._get_lock_file_path()

        if not os.path.exists(lock_file_path):
            self.logger.warning(
                "Attempt to remove a lock of inexistent lock on "
                "event id: {}".format(self.event.pk))
            return
        self.logger.info(
            "Removing lock file for event id: {}".format(self.event.pk))
        os.remove(lock_file_path)

    def has_existing_export_files(self) -> bool:
        exporter_folder_path = self._get_exporter_folder_path()

        if not os.path.isdir(exporter_folder_path):
            return False

        for file in os.listdir(exporter_folder_path):
            if file.endswith(".xlsx"):
                return True

        return False

    def create_export_file(self, payload: bytes) -> None:
        exporter_folder_path = self._get_exporter_folder_path()
        exporter_file_path = exporter_folder_path + 'cgsy.xlsx'

        if not os.path.isdir(exporter_folder_path):
            self.logger.info(
                "Creating exporter lock folder for event id: {}".format(
                    self.event.pk
                ))
            os.makedirs(exporter_folder_path)

        f = open(exporter_file_path, 'wb')
        f.write(payload)
        f.close()
        self.logger.info(
            "Created export file '{}' for event id: {}".format(
                exporter_file_path,
                self.event.pk,
            )
        )

    def remove_export_files(self) -> None:
        exporter_folder_path = self._get_exporter_folder_path()

        for file in os.listdir(exporter_folder_path):
            if file.endswith(".xlsx"):
                self.logger.info(
                    "Removing export file '{}' for event id: {}".format(
                        file,
                        self.event.pk
                    ))
                os.remove(exporter_folder_path + file)

    def get_export_file_path(self) -> str:
        return self._get_exporter_folder_path() + 'cgsy.xlsx'

    def _get_lock_file_path(self) -> str:
        return self._get_exporter_folder_path() + 'cgsy.lock'

    def _get_exporter_folder_path(self) -> str:
        media_url = settings.MEDIA_ROOT
        return media_url + self.exporter_url + '{}/'.format(self.event.pk)
