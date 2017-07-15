""" Formulários de `Field` """
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.forms import ModelForm, model_to_dict
from django.forms.fields import Field as FormField

from gatheros_event.models import Organization
from gatheros_subscription.models import Field
from kanu_form.forms import KanuForm


class FieldsRendererMixin(KanuForm):
    """
    Mixin para exibir formulário do Django contruído a partir de dados de
    modelos `Fields`.
    """

    def __init__(self, *args, **kwargs):
        self.gatheros_fields = {}
        self.default_fields = {}
        self.additional_fields = {}

        super(FieldsRendererMixin, self).__init__(*args, **kwargs)
        self._create_fields()

    def is_default(self, field_name):
        """
        Verifica se o campo é padrão.
        :type field_name: str
        :rtype: bool
        """
        return field_name in self.default_fields

    def get_form_field_by_name(self, field_name):
        """
        Resgata form field pelo nome único.
        :type field_name: str
        :rtype: FormField
        """
        return self.fields[field_name] if field_name in self.fields else None

    def get_gatheros_field_by_name(self, field_name):
        """
        Resgata gatheros field pelo nome único.
        :type field_name: str
        :rtype: Field
        """
        return self.gatheros_fields.get(field_name)

    def _get_fields_queryset(self):
        """
        Resgata queryset de `Field` para criar campos.
        :rtype: QuerySet
        """
        raise NotImplementedError(
            'Você deve implementar este método para definir quais campos serão'
            ' utilizados para a criação dos campos do formulário do Django.'
        )

    def _create_fields(self):
        """
        Cria campos do formulário a partir dos dados do model `Field`.
        """
        for gatheros_field in self._get_fields_queryset():
            self.gatheros_fields[gatheros_field.name] = gatheros_field

            if gatheros_field.form_default_field:
                self.default_fields[gatheros_field.name] = gatheros_field
            else:
                self.additional_fields[gatheros_field.name] = gatheros_field

            data = self._get_gatheros_field_dict(gatheros_field)
            self.create_field(**data)

    @staticmethod
    def _get_gatheros_field_dict(gatheros_field):
        """
        Resgata dict de `Field` com a estrutura correta.

        :type gatheros_field: Field
        :rtype: dict
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


class OrganizationFieldsForm(FieldsRendererMixin):
    """ Formulário de formatação para campos de organização. """

    def __init__(self, organization, *args, **kwargs):
        """
        :type organization: Organization
        """
        self.organization = organization
        super(OrganizationFieldsForm, self).__init__(*args, **kwargs)

    def _get_fields_queryset(self):
        queryset = self.organization.fields.annotate(
            num_forms=Count('forms'),
            num_answers=Count('answers')
        ).filter(
            organization=self.organization,
            form_default_field=False,
        ).order_by('-num_answers', '-num_forms')

        return queryset


class FieldForm(ModelForm):
    """ Formulário de Campo de Organização. """
    organization = None

    class Meta:
        """ Meta """
        model = Field
        fields = (
            'field_type',
            'label',
            'placeholder',
            'required',
            'select_intro',
            'instruction',
            'default_value',
            # 'active',
        )

    def __init__(self, organization, *args, **kwargs):
        """
        :type organization: Organization
        """
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
        """ Salva dados. """
        self.instance.organization = self.organization
        return super(FieldForm, self).save(commit)
