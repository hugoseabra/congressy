from django.core.exceptions import ValidationError
import os


def validate_csv_only_file(value):

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename

    valid_extensions = [
        '.csv'
    ]

    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Tipo de arquivo não permitido.')