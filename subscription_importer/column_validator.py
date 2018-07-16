from .constants import KEY_MAP


class ColumnValidator(object):

    def __init__(self, column: list) -> None:
        self.column = column
        self.valid = False
        self.valid_columns = []
        self.invalid_columns = []
        super().__init__()

    def clean(self):

        for col in self.column:

            is_valid = False

            parsed_entry = col.lower().strip()

            for key, value in KEY_MAP.items():
                if parsed_entry in value['csv_keys']:
                    is_valid = True
                    break

            if is_valid:
                self.valid_columns.append(parsed_entry)
            else:
                self.invalid_columns.append(col)

    def has_valid(self):
        self.clean()
        if len(self.valid_columns) > 0:
            self.valid = True
            return True

        return False
