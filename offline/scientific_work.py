from .base import Base, EraserMixin


class ScientificWorkOffline(Base, EraserMixin):
    erase_list = [
        'scientific_work.Work',
        'scientific_work.WorkConfig',
        'scientific_work.Author',
        'scientific_work.AreaCategory',
    ]
