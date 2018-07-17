import csv


class DataFileTransformer(object):
    """
        Essa classe possui a responsabilidade de abrir, ler um arquivo e
        retornar o conteudo que podem ser:
            - conteudo linha a linha
            - cabeçalho

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

    def get_lines(self, size: int = 20) -> list:
        lines = []

        counter = 0
        for line in self._get_reader():
            lines.append(line)
            if counter == size:
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
