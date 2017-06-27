from collections import OrderedDict

from kanu_form.fields.field import Field


class FieldManager(object):
    def __init__(self):
        super(FieldManager, self).__init__()
        self.fields = OrderedDict()
        self.kanu_fields = OrderedDict()

    def create(self, name, field_type, initial=None, required=True,
               label=None, **kwargs):
        field = Field(
            field_type,
            initial,
            required,
            label,
            **kwargs
        )
        self.fields.update({name: field.get_django_field()})
        self.kanu_fields.update({name: field})

        return field
