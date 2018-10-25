from collections import Iterator
from datetime import datetime


class TransactionStatusCollection(Iterator):
    """ Collection de mudanças de status de uma Transação. """

    def __init__(self):
        self.items = list()
        self.current = 0

    def add(self, created_on: datetime, status: str, data: dict) -> None:
        self.items.append({
            'created': created_on,
            'status': status,
            'data': data,
        })

    def last(self):
        if not self.items:
            return None

        return self.items[-1]

    def __getitem__(self, item) -> dict:
        if item >= len(self):
            raise IndexError("Out of range")
        return self.current + item

    def __len__(self) -> int:
        return len(self.items)

    def __next__(self) -> dict:
        self.current += 1

        try:
            return self.items[self.current - 1]
        except IndexError:
            self.current = 0
            # Done iterating.
            raise StopIteration
