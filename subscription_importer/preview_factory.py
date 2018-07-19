from subscription_importer import (
    LineData,
    NoValidLinesError,
)


class PreviewFactory(object):
    """
        Essa classe serve como helper para as view que a usa para gerar preview 
        dos dados passados para essa factory. 
    """

    def __init__(self, data_list: list, ) -> None:

        self.data_list = data_list

        self.parsed_lines = self._parse_data()
        self.table = self._make_html_table()
        self.invalid_keys = self._get_invalid_keys()

    def _parse_data(self):

        parsed_lines = []
        for line in self.data_list:
            parsed_lines.append(LineData(raw_data=line))

        if len(parsed_lines) == 0:
            raise NoValidLinesError()

        return parsed_lines

    def _make_html_table(self):

        first_line = self.parsed_lines[0]

        table_heading = ''
        table_body = ''

        for key, _ in first_line:
            table_heading += '<th>' + key.title() + '</th>'

        for line in self.parsed_lines:
            table_body += '<tr>'
            for _, value in line:
                table_body += '<td>'
                table_body += value
                table_body += '</td>'

            table_body += '</tr>'

        table = '<table class="table"><thead><tr>' + \
                table_heading + '</tr></thead><tbody>' + table_body + \
                '</tbody></table>'

        return table

    def _get_invalid_keys(self):
        first_line = self.parsed_lines[0]
        return first_line.get_invalid_keys()
