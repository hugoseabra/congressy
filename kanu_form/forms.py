from django import forms
from django.forms import model_to_dict
from django.utils import six


class KanuForm(forms.Form):
    """ Formulário Dinâmico. """

    field_manager = None

    def __init__(self, field_manager, *args, **kwargs):
        self.field_manager = field_manager
        super(KanuForm, self).__init__(*args, **kwargs)
        self._add_fields()

    def _add_fields(self):
        self.fields.keyOrder = []
        for name, django_field in six.iteritems(self.field_manager.fields):
            self.fields[name] = django_field
            self.fields.keyOrder.append(name)

    @staticmethod
    def get_field_dict(gatheros_field):
        """
        Resgata dict de `Field` com a estrutura correta.

        :param gatheros_field: `gatheros_subscription.models.Field`
        :return: Dict
        """
        field_dict = model_to_dict(gatheros_field, exclude=[
            'active',
            'default_value',
            'form_default_field',
            'form',
            'id',
            'instruction',
            'order',
            'with_options',
        ])

        field_dict['help_text'] = gatheros_field.instruction

        if gatheros_field.default_value:
            field_dict['initial'] = gatheros_field.default_value

        if gatheros_field.with_options:
            field_dict['options'] = [
                (opt.value, opt.name) for opt in gatheros_field.options.all()
            ]

        return field_dict
