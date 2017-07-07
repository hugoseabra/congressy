from django.db.models import Count
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm

from gatheros_subscription.models import Field
from kanu_form.field_manager import FieldManager
from kanu_form.forms import KanuForm


class FieldsForm(KanuForm):
    """ Formulário de formatação para campos de organização. """
    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        self.gatheros_fields = {}

        # Prepare fields to render
        self.field_manager = FieldManager()
        self._configure_fields()

        super(FieldsForm, self).__init__(self.field_manager, *args, **kwargs)

    def get_gatheros_field_by_name(self, field_name):
        """ Resgata gatheros field pelo nome único. """
        try:
            return self.organization.fields.get(name=field_name)

        except Field.DoesNotExist:
            return None

    def _configure_fields(self):
        """ Configura campos do formulário dinamicamente. """

        queryset = self.organization.fields.annotate(
            num_forms=Count('forms'),
            num_answers=Count('answers'),
        ).filter(
            organization=self.organization,
            form_default_field=False,
        ).order_by('-num_answers', '-num_forms')

        for f in queryset:
            self.gatheros_fields[f.name] = f
            self.field_manager.create(**self.get_field_dict(f))


class FieldForm(ModelForm):
    """ Formulário de Campo de Organização. """
    organization = None

    class Meta:
        model = Field
        fields = (
            'field_type',
            'label',
            'placeholder',
            'required',
            'select_intro',
            'instruction',
            'default_value',
            'active',
        )

    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        super(FieldForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            if self.instance.organization != self.organization:
                raise PermissionDenied(
                    'Este campo não pertence à organização "{}"'.format(
                        self.organization.name
                    )
                )

            if self.instance.form_default_field is True:
                raise PermissionDenied('Este campo não pode ser editado.')

    def save(self, commit=True):
        self.instance.organization = self.organization
        return super(FieldForm, self).save(commit)
