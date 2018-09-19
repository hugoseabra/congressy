import os
from datetime import datetime

from django.conf import settings


class TransactionLog(object):
    def __init__(self, id) -> None:
        self.id = id
        self.created = self.get_datetime()
        self.file_name = 'transaction_log-{}_{}.log'.format(
            id,
            self.created.strftime('%Y%m%d-%H%M%S')
        )
        self.content = ''
        self.lines = []

    def get_datetime(self):
        return datetime.now()

    def fetch(self):
        file_path = self._get_file_path()
        with open(file_path, 'r') as f:
            self.content = f.read()
            f.close()

        return self.content

    def add_message(self, msg, save=False):
        self.lines.append('{}: {}'.format(self.get_datetime(), msg))

        if save is True:
            self.save()

    def _get_file_path(self):
        if not os.path.isdir(settings.CGSY_LOGS_DIR):
            os.mkdir(settings.CGSY_LOGS_DIR)

        transaction_logs_dir_path = os.path.join(
            settings.CGSY_LOGS_DIR,
            'transactions'
        )
        if not os.path.isdir(transaction_logs_dir_path):
            os.mkdir(transaction_logs_dir_path)

        return os.path.join(transaction_logs_dir_path, self.file_name)

    def delete(self):
        file_path = self._get_file_path()

        if os.path.isfile(file_path):
            os.remove(file_path)

    def save(self):
        file_path = self._get_file_path()

        if not self.lines:
            return

        with open(file_path, 'a') as f:
            for add_line in self.lines:
                content = add_line + "\n"
                f.write(content)
                self.content += content

            f.close()

        self.lines = []
