from django import forms
from django.forms import model_to_dict

from gatheros_subscription.models import Field, FieldOption
from kanu_form.field_manager import FieldManager
from kanu_form.forms import KanuForm


class EventConfigForm(KanuForm):
    default_fields = set()
    additional_fields = set()
    gatheros_fields = {}
    fields_configured = False
    include_inactive = False

    def __init__(
            self,
            form,
            field_manager=None,
            include_inactive=False,
            *args,
            **kwargs):

        self.form = form

        if not field_manager:
            self.field_manager = FieldManager()

        self.include_inactive = include_inactive

        self.configure_fields()
        super(EventConfigForm, self).__init__(
            self.field_manager,
            *args,
            **kwargs
        )

    def is_default(self, field_name):
        """ Verifica se o campo é padrão. """
        return field_name in self.default_fields

    def get_gatheros_field_by_name(self, field_name):
        """ Resgata gatheros field pelo nome único. """
        try:
            return self.form.fields.get(name=field_name)
        except Field.DoesNotExist:
            return None

    def get_form_field_by_name(self, field_name):
        """ Resgata form field pelo nome único. """
        return self.fields[field_name] if field_name in self.fields else None

    def configure_fields(self):
        """ Configura campos do formulário dinamicamente. """

        if self.fields_configured:
            return

        fields_qs = self.form.fields

        if not self.include_inactive:
            fields_qs = fields_qs.filter(active=True)

        for f in fields_qs.all():
            self.gatheros_fields[f.name] = f

            if f.form_default_field:
                self.default_fields.add(f.name)
            else:
                self.additional_fields.add(f.name)

            field_dict = model_to_dict(f, exclude=[
                'active',
                'default_value',
                'form_default_field',
                'form',
                'id',
                'instruction',
                'order',
                'with_options',
            ])

            field_dict['help_text'] = f.instruction

            if f.default_value:
                field_dict['initial'] = f.default_value

            if f.with_options:
                field_dict['options'] = [
                    (opt.value, opt.name) for opt in f.options.all()
                ]

            self.field_manager.create(**field_dict)

        self.fields_configured = True


class EventFormFieldForm(forms.ModelForm):
    form = None

    class Meta:
        model = Field
        fields = [
            'field_type',
            'name',
            'label',
            'placeholder',
            'required',
            'instruction',
            'default_value',
            'active',
        ]

    def __init__(self, form, *args, **kwargs):
        self.form = form
        super(EventFormFieldForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            if instance.form_default_field is True:
                raise forms.ValidationError('Este campo não pode ser editado')

            if instance.form.event.pk != form.event.pk:
                raise forms.ValidationError(
                    'Este campo não pertence ao formulário `{}`'.format(form)
                )

    def save(self, commit=True):
        self.instance.form = self.form
        self.instance.form_default_field = False

        return super(EventFormFieldForm, self).save(commit=commit)


class EventFormFieldOrderForm(forms.Form):
    instance = None
    fields_qs = None

    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        self.fields_qs = self.instance.form.fields

        self.current_order = self.instance.order
        super(EventFormFieldOrderForm, self).__init__(*args, **kwargs)

    def order_down(self):
        """
        Ordena com ordem decrecente o Field da instanciado form e ajusta o
        Field posterior para cima.
        """
        order = self.instance.order
        previous_field = self.get_previous_field(order)

        if not previous_field:
            return self.instance

        self.instance.order = previous_field.order
        previous_field.order = previous_field.order + 1

        previous_field.save()
        self.instance.save()

        return self.instance

    def order_up(self):
        """
        Ordena com ordem crecente o Field da instanciado form e ajusta o Field
        posterior para baixo.
        """
        order = self.instance.order
        next_field = self.get_next_field(order)

        if not next_field:
            return self.instance

        self.instance.order = next_field.order
        next_field.order = next_field.order - 1

        next_field.save()
        self.instance.save()

        return self.instance

    def get_previous_field(self, current_order):
        """ Resgata o campo anterior mais próximo. """
        try:
            return self.fields_qs.filter(
                form_default_field=False,
                order__lt=current_order
            ).order_by('-order').first()

        except Field.DoesNotExist:
            return None

    def get_next_field(self, current_order):
        """ Resgata o campo posterior mais próximo. """
        try:
            return self.fields_qs.filter(
                form_default_field=False,
                order__gt=current_order
            ).order_by('order').first()

        except Field.DoesNotExist:
            return None


class EventFormFieldOptionForm(forms.ModelForm):
    """ Formulário de opção de campo de formulário. """

    class Meta:
        model = FieldOption
        fields = ['name', 'value']

    def __init__(self, field, *args, **kwargs):
        self.field = field
        super(EventFormFieldOptionForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.instance.pk and self.instance.field.pk != self.field.pk:
            raise forms.ValidationError('Você não pode editar esta opção.')

        return super(EventFormFieldOptionForm, self).clean()

    def save(self, commit=True):
        self.full_clean()

        self.instance.field = self.field
        return super(EventFormFieldOptionForm, self).save(commit=commit)
