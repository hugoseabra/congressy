from .column_validator import ColumnValidator


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
            column_validator: ColumnValidator,
            *args: object,
            **kwargs: object) -> None:
        self.column_validator = column_validator
        super().__init__(*args, **kwargs)


class NoValidLinesError(Exception):
    pass


class MappingNotFoundError(Exception):
    def __init__(self, key, *args: object, **kwargs: object) -> None:
        self.message = '{} not found'.format(key)
        self.key = key
        super().__init__(*args, **kwargs)
