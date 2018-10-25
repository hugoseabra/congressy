from core.util.collection import merge_lists_ignore_duplicates
from gatheros_subscription.models import Lot
from importer.constants import KEY_MAP, extract_key_by_verbose_name
from importer.line_data import LineDataCollection


class PreviewBuilder(object):
    """
        Essa classe serve como helper para as view que a usa para gerar preview  
    """

    def __init__(self, ldc: LineDataCollection, lot: Lot):
        self.line_data_collection = ldc
        self.lot = lot

    def _get_header(self, survey=None) -> list:
        headers = list()
        survey_headers = list()

        if len(self.line_data_collection) > 0:

            for key, _ in self.line_data_collection[0]:
                headers.append(KEY_MAP[key]['verbose_name'])

            for line_data in self.line_data_collection:
                for item in line_data.get_survey_keys(survey):
                    if item['key'] not in survey_headers:
                        survey_headers.append(item['key'])

        return merge_lists_ignore_duplicates(
            headers,
            survey_headers,
        )

    def render_html_table(self):

        table_heading = ''
        table_body = ''
        header = list()
        survey = None

        if self.lot.event_survey:
            survey = self.lot.event_survey.survey

        if len(self.line_data_collection) > 1:
            header = self._get_header(survey=survey)

        for item in header:
            table_heading += '<th>' + item.title() + '</th>'

        for line in self.line_data_collection:
            table_body += '<tr>'

            for key in header:

                clean_key = extract_key_by_verbose_name(key)
                value = None

                if clean_key:
                    value = line.get(clean_key)

                if not clean_key:

                    for item in line.get_survey_keys(survey):
                        if key == item['key']:
                            value = item['value']

                if not value:
                    value = "---"

                table_body += '<td>'
                table_body += value
                table_body += '</td>'

            table_body += '</tr>'

        table = '<table class="table"><thead><tr>' + \
                table_heading + '</tr></thead><tbody>' + table_body + \
                '</tbody></table>'

        return table
