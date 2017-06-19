# from kanu_form.fields.field import Field
from django.forms import model_to_dict

from kanu_form.field_manager import FieldManager
from kanu_form.forms import KanuForm


class EventForm(KanuForm):
    default_fields = set()

    def __init__(self, event, *args, **kwargs):
        self.event = event
        self.field_manager = FieldManager()
        self._configure_fields()
        super(EventForm, self).__init__(self.field_manager, *args, **kwargs)

    def is_default(self, field_name):
        """ Verifica se o campo é padrão. """
        return field_name in self.default_fields

    def _configure_fields(self):
        """ Configura campos do formulário dinamicamente. """

        fields = self.event.form.fields.filter(active=True)

        for field in fields:
            field_dict = model_to_dict(field, exclude=[
                'active',
                'id',
                'instruction',
                'form_default_field',
                'form',
                'with_options',
                'order',
            ])
            field_dict['help_text'] = field.instruction

            if field.with_options:
                field_dict['options'] = [(option.value, option.name) for option
                                         in field.options.all()]

            if field.form_default_field:
                self.default_fields.add(field.name)

            self.field_manager.create(**field_dict)
