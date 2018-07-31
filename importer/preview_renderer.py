from subscription_importer import (
    KEY_MAP,
)

from subscription_importer.line_data import LineDataCollection


class PreviewRenderer(object):
    """
        Essa classe serve como helper para as view que a usa para gerar preview 
        dos dados passados para essa factory. 
    """

    def __init__(self, line_data_collection: LineDataCollection):
        self.line_data_collection = line_data_collection

    def render_html_table(self):

        first_line = self.line_data_collection[0]

        table_heading = ''
        table_body = ''

        header_names = []
        for key, _ in first_line:
            header_names.append(KEY_MAP[key]['verbose_name'])

        for key in header_names:
            table_heading += '<th>' + key.title() + '</th>'

        for line in self.line_data_collection:
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
