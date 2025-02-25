from .line_data import LineData


class DataColumnError(Exception):

    def __init__(self,
                 column_name: str,
                 error: str,
                 *args: object,
                 **kwargs: object) -> None:
        self.column_name = column_name
        self.error = error

        self.message = '{}: {}'.format(column_name, error)
        super().__init__(*args, **kwargs)


class NoValidColumnsError(Exception):

    def __init__(
            self,
            line_data: LineData,
            *args: object,
            **kwargs: object) -> None:
        self.line_data = line_data
        super().__init__(*args, **kwargs)



