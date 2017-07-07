from django import forms
from django.core.exceptions import PermissionDenied

from gatheros_subscription.models import FieldOption


class FieldOptionForm(forms.ModelForm):
    """ Formulário de opção de campo de formulário. """

    class Meta:
        model = FieldOption
        fields = ('name', 'value',)

    def __init__(self, field, *args, **kwargs):
        self.field = field
        super(FieldOptionForm, self).__init__(*args, **kwargs)

        if self.instance.pk and self.instance.field.pk != self.field.pk:
            raise PermissionDenied('Você não pode editar esta opção.')

        default_field = self.field.form_default_field is True
        field_supports_option = self.field.with_options
        if default_field or not field_supports_option:
            raise PermissionDenied('Você não pode editar esta opção.')

    def save(self, commit=True):
        self.instance.field = self.field
        return super(FieldOptionForm, self).save(commit=commit)
