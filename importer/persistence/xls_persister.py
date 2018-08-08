import abc
import json
import locale
from collections import OrderedDict
from csv import DictReader

from openpyxl import Workbook, styles
from openpyxl.comments import Comment
from openpyxl.styles import colors
from six import BytesIO

from core.util import merge_lists_ignore_duplicates
from importer.constants import KEY_MAP
from importer.helpers import get_mapping_from_csv_key, MappingNotFoundError
from survey.models import Question


class XLSPersister(abc.ABC):

    def __init__(self, csv_file_path) -> None:
        self.file_path = csv_file_path
        self._reader = None

    def _get_reader(self) -> DictReader:
        self._reader = DictReader(open(self.file_path, 'r'))

        return self._reader

    @abc.abstractmethod
    def _get_header(self) -> list:
        pass

    @abc.abstractmethod
    def make(self) -> bytes:
        pass


class XLSErrorPersister(XLSPersister):

    def __init__(self, csv_file_path) -> None:
        super().__init__(csv_file_path)
        self.redFill = styles.PatternFill(
            patternType='solid',
            fill_type='solid',
            start_color=colors.RED,
            end_color=colors.RED,
        )

    def _get_header(self, survey=None) -> list:

        form_keys = []
        headers = []
        survey_headers = []
        if survey:
            questions = Question.objects.filter(
                survey=survey,
            ).order_by('order')

            for question in questions:
                cleaned_label = question.label.lower().strip().replace('?', '')
                survey_headers.append(cleaned_label)

        for line in self._get_reader():

            raw_data = json.loads(line['raw_data'])

            raw_data_keys = raw_data.keys()
            for key in raw_data_keys:
                if key not in form_keys:
                    form_keys.append(key)

        for key in form_keys:
            if key not in survey_headers:
                headers.append(KEY_MAP[key]['csv_keys'][0])

        return merge_lists_ignore_duplicates(headers, survey_headers)

    def make(self, survey=None) -> bytes:

        headers = self._get_header(survey)

        cell_mapping = OrderedDict()
        i = 0
        for key in headers:
            letter = chr(ord('a') + i)
            cell_mapping.update({key: letter.upper()})
            i += 1

        stream = BytesIO()

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        wb = Workbook()

        ws1 = wb.active
        ws1.title = 'Inscrições com erros'

        ws1.append(headers)

        line_counter = 2

        for line in self._get_reader():
            raw_data = json.loads(line['raw_data'])
            errors = json.loads(line['errors'])

            for key in headers:
                cell = cell_mapping[key] + str(line_counter)
                if survey:
                    try:
                        form_key, _ = get_mapping_from_csv_key(key)
                    except MappingNotFoundError:
                        form_key = key
                else:
                    form_key, _ = get_mapping_from_csv_key(key)

                if form_key in raw_data:

                    value = raw_data[form_key]

                    if value == "":
                        value = ''

                    ws1[cell] = value
                else:
                    ws1[cell] = ''

                if form_key in errors:
                    ws1[cell].fill = self.redFill
                    ws1[cell].comment = Comment(errors[form_key], 'Congressy')

            line_counter += 1

        wb.save(stream)

        return stream.getvalue()
