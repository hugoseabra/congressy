from django.core.exceptions import FieldError
from django.forms import fields
from django.forms import widgets

from .widgets import DateInput, DateTimeInput, EmailInput, TelInput


class Field(object):
    placeholder = None
    help_text = None
    value = None
    max_length = 255

    FIELD_INPUT_TEXT = 'input-text'
    FIELD_INPUT_NUMBER = 'input-number'
    FIELD_INPUT_DATE = 'input-date'
    FIELD_INPUT_DATETIME = 'input-datetime-local'
    FIELD_INPUT_EMAIL = 'input-email'
    FIELD_INPUT_PHONE = 'input-phone'
    FIELD_TEXTAREA = 'textarea'
    FIELD_BOOLEAN = 'boolean'
    FIELD_SELECT = 'select'
    FIELD_CHECKBOX_GROUP = 'checkbox-group'
    FIELD_RADIO_GROUP = 'radio-group'

    supported_types = [
        FIELD_INPUT_TEXT,
        FIELD_INPUT_NUMBER,
        FIELD_INPUT_DATE,
        FIELD_INPUT_DATETIME,
        FIELD_INPUT_EMAIL,
        FIELD_INPUT_PHONE,
        FIELD_TEXTAREA,
        FIELD_BOOLEAN,
        FIELD_SELECT,
        FIELD_CHECKBOX_GROUP,
        FIELD_RADIO_GROUP
    ]

    def __init__(self, field_type, initial=None, required=True, label=None,
                 **kwargs):

        if field_type in self.supported_types:
            self.type = field_type
        else:
            raise FieldError('`{}` não é um campo permitido: '.format(
                field_type,
                ', '.join(self.supported_types)
            ))

        self.initial = initial
        self.required = required
        self.label = label
        self.placeholder = kwargs.get('placeholder', '')
        self.help_text = kwargs.get('help_text', '')
        self.max_length = kwargs.get('max_length', 255)
        self.select_intro = kwargs.get('select_intro', False)
        self.attrs = kwargs.get('attrs', {})
        self.options = kwargs.get('options', [])

    def get_django_field(self):
        field = None

        if self.type == self.FIELD_INPUT_TEXT:
            field = fields.CharField(
                max_length=self.max_length,
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(fields.TextInput)
            )

        if self.type == self.FIELD_INPUT_NUMBER:
            field = fields.CharField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(fields.NumberInput)
            )

        if self.type == self.FIELD_INPUT_DATE:
            field = fields.DateField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(DateInput, format='%d/%m/%Y')
            )

        if self.type == self.FIELD_INPUT_DATETIME:
            field = fields.CharField(
                max_length=18,
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(
                    DateTimeInput,
                    format='%d/%m/%Y %H:%M:%S'
                )
            )

        if self.type == self.FIELD_INPUT_EMAIL:
            field = fields.EmailField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(EmailInput)
            )

        if self.type == self.FIELD_INPUT_PHONE:
            field = fields.CharField(
                max_length=18,
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(TelInput)
            )

        if self.type == self.FIELD_BOOLEAN:
            field = fields.BooleanField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(fields.CheckboxInput)
            )

        if self.type == self.FIELD_SELECT:
            field = fields.ChoiceField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(widgets.Select)
            )

            if self.select_intro:
                intro_option = [('', '- Selecione -',)]
                self.options = intro_option + self.options

        if self.type == self.FIELD_RADIO_GROUP:
            field = fields.ChoiceField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(widgets.RadioSelect)
            )

        if self.type == self.FIELD_CHECKBOX_GROUP:
            field = fields.MultipleChoiceField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(widgets.CheckboxSelectMultiple)
            )

        if self.type == self.FIELD_TEXTAREA:
            field = fields.ChoiceField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(widgets.Textarea)
            )

        if not field:
            raise FieldError('`{}` não encontrado: '.format(self.type))

        if self.options:
            field.choices = self.options

        field.test = 1

        return field

    def _get_widget(self, widget_class, **kwargs):
        if self.required:
            self.attrs.update({
                'required': self.required
            })

        if self.placeholder:
            self.attrs.update({
                'placeholder': self.placeholder
            })

        if self.attrs:
            kwargs.update({'attrs': self.attrs})

        return widget_class(**kwargs)
