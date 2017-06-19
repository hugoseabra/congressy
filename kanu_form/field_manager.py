from kanu_form.fields.field import Field

from collections import OrderedDict


class FieldManager(object):
    def __init__(self):
        super(FieldManager, self).__init__()
        self.fields = OrderedDict()

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
        return field
