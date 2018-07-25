import abc
import csv
import json

from django.core.files.base import ContentFile

from subscription_importer.line_data import LineDataCollection


class CSVPersister(abc.ABC):

    def __init__(self, line_data_collection: LineDataCollection) -> None:
        self._file = ContentFile('')
        self.line_data_collection = line_data_collection

    @abc.abstractmethod
    def write(self) -> ContentFile:
        pass


class CSVErrorPersister(CSVPersister):

    def write(self) -> ContentFile:

        writer = csv.DictWriter(self._file, fieldnames=['raw_data', 'errors'])
        writer.writeheader()

        for line in self.line_data_collection:

            raw_data = {}
            for key, value in line:
                raw_data.update({key: value})

            errors = {}
            for fieldname, error_list in line.get_errors().items():

                if fieldname == '__all__':
                    continue

                error = error_list[0]
                errors.update({fieldname: error})

            raw_data = json.dumps(raw_data, ensure_ascii=False)
            errors = json.dumps(errors, ensure_ascii=False)

            data = {
                'raw_data': raw_data,
                'errors': errors,
            }

            writer.writerow(data)

        return self._file
