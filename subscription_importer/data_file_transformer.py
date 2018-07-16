import csv


class DataFileTransformer(object):

    def __init__(self,
                 file_path: str,
                 delimiter: str,
                 separator: str,
                 encoding: str, ) -> None:

        # This might raise a decoding error
        self.reader = csv.DictReader(
            open(file_path, 'r', encoding=encoding),
            delimiter=delimiter,
            quotechar=separator,
        )

        super().__init__()

    def get_dict_list(self) -> list:
        dict_list = []

        for line in self.reader:
            dict_list.append(line)

        return dict_list

    def get_columns(self) -> list:
        return self.reader.fieldnames
