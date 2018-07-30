"""
    Essa classe serve como um objeto de Collection(Container) para guardar
    objetos e objetos do subtipo di tipo LineData
"""

from collections import UserList

from .line_data import LineData


class NoValidLinesError(Exception):
    pass


class LineDataCollection(UserList):
    """
        Uma coleção(container) de objetos do tipo LineData
    """

    def __init__(self):

        self.data = []
        super().__init__()

        if not self.data:
            raise NoValidLinesError()

    def append(self, line: LineData):

        if not isinstance(line, LineData):
            raise ValueError('{} não é do tipo LineData'.format(type(line)))

        self.data.append(line)
