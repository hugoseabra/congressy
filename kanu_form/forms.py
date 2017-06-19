from django import forms
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
        for name, field in six.iteritems(self.field_manager.fields):
            self.fields[name] = field
            self.fields.keyOrder.append(name)
