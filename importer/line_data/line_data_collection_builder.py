import csv

from importer.line_data import LineDataCollection, LineData


class LineDataCollectionBuilder(object):
    """
        Essa classe possui a responsabilidade de abrir, ler um arquivo e
        retornar uma coleção de objetos do tipo LineData
        chamado LineDataCollection
    """

    def __init__(self,
                 file_path: str,
                 delimiter: str,
                 separator: str,
                 encoding: str, ) -> None:

        self.file_path = file_path
        self.delimiter = delimiter
        self.separator = separator
        self.encoding = encoding

        self._reader = None

    def get_collection(self, size: int = 0) -> LineDataCollection:
        lines = LineDataCollection()

        counter = 1
        for line in self._get_reader():
            lines.append(LineData(line))

            if size != 0 and counter == size:
                break

            counter += 1

        return lines

    def get_header(self) -> list:
        return self._get_reader().fieldnames

    def _get_reader(self):
        if self._reader:
            return self._reader

        # This might raise a decoding error
        self._reader = csv.DictReader(
            open(self.file_path, 'r', encoding=self.encoding),
            delimiter=self.delimiter,
            quotechar=self.separator,
        )

        return self._reader
