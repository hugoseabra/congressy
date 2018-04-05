from __future__ import unicode_literals

from django.core.exceptions import FieldError
from django.forms import fields, widgets, SelectDateWidget

from core.forms.widgets import DateTimeInput, TelephoneInput
from core.util.date import create_years_list


class SurveyField(object):
    django_field = None
    placeholder = None
    help_text = None
    value = None
    max_length = None
    question = None

    # TODO: Remove this use from constants.py

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

    def __init__(self, question, field_type, initial=None, required=True,
                 label=None,
                 **kwargs):

        self.question = question

        if field_type in self.supported_types:
            self.type = field_type

        else:
            raise FieldError('`{}` não é um campo permitido: '.format(
                field_type,
                ', '.join(self.supported_types)
            ))

        options = []

        if question.has_options:
            options = [(opt.value, opt.name) for opt in
                       question.options.all().order_by('pk')]

        self.initial = initial
        self.required = required
        self.can_edit = True
        self.label = label or ''
        self.placeholder = kwargs.get('placeholder', '')
        self.help_text = kwargs.get('help_text', '')
        self.max_length = kwargs.get('max_length', 255)
        self.select_intro = kwargs.get('select_intro', False)
        self.attrs = kwargs.get('attrs', {})
        self.options = options

    def get_django_field(self):
        """ Recupera campo do Django Forms correto de acordo com o tipo. """

        if self.type == self.FIELD_INPUT_TEXT:
            self.django_field = fields.CharField(
                max_length=self.max_length,
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_INPUT_NUMBER:
            self.django_field = fields.CharField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_INPUT_DATE:
            self.django_field = fields.DateField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(),
            )

        if self.type == self.FIELD_INPUT_DATETIME:
            self.django_field = fields.CharField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_INPUT_EMAIL:
            self.django_field = fields.EmailField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_INPUT_PHONE:
            self.django_field = fields.CharField(
                max_length=18,
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_BOOLEAN:
            self.django_field = fields.BooleanField(
                label=self.label.title(),
                initial=self.initial,
                required=False,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_SELECT:
            self.django_field = fields.ChoiceField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_TEXTAREA:
            self.django_field = fields.CharField(
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_RADIO_GROUP:
            self.django_field = fields.ChoiceField(
                label=self.label.title(),
                initial=self.initial,
                required=False,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_CHECKBOX_GROUP:
            self.django_field = fields.MultipleChoiceField(
                label=self.label.title(),
                initial=self.initial,
                required=self.required,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if not self.django_field:
            raise FieldError('`{}` não encontrado: '.format(self.type))

        if self.options:
            self.django_field.choices = self.options

        self.django_field.can_edit = not self.question.has_answers
        self.django_field.field_type = self.type
        self.django_field.question_id = self.question.pk

        return self.django_field

    def _get_widget(self):
        """ Recupera o Widget correto de acordo com o tipo de campo. """

        widget = None

        if self.type == self.FIELD_INPUT_TEXT:
            widget = self._configure_widget(widgets.TextInput)

        if self.type == self.FIELD_INPUT_NUMBER:
            widget = self._configure_widget(widgets.NumberInput)

        if self.type == self.FIELD_INPUT_DATE:
            widget = SelectDateWidget(
                attrs=({'style': 'width: 30%; display: inline-block;'}),
                years=create_years_list(),
            )

        if self.type == self.FIELD_INPUT_DATETIME:
            widget = self._configure_widget(
                DateTimeInput,
                format='%d/%m/%Y %H:%M:%S'
            )

        if self.type == self.FIELD_INPUT_EMAIL:
            widget = self._configure_widget(fields.EmailInput)

        if self.type == self.FIELD_INPUT_PHONE:
            widget = self._configure_widget(TelephoneInput)

        if self.type == self.FIELD_BOOLEAN:
            widget = self._configure_widget(widgets.CheckboxInput)

        if self.type == self.FIELD_SELECT:
            widget = self._configure_widget(widgets.Select)

            if self.select_intro:
                intro_option = [('', '- Selecione -',)]
                self.options = intro_option + self.options

        if self.type == self.FIELD_TEXTAREA:
            widget = self._configure_widget(widgets.Textarea)

        if self.type == self.FIELD_RADIO_GROUP:
            widget = self._configure_widget(widgets.RadioSelect)

        if self.type == self.FIELD_CHECKBOX_GROUP:
            widget = self._configure_widget(widgets.CheckboxSelectMultiple)

        return widget

    def _configure_widget(self, widget_class, **kwargs):
        """ Configura widget inserindo parâmetros necessários. """

        if self.has_requirement() and self.required:
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

    def has_requirement(self):
        """ Verifica se campos possuem atributo `required`. """
        not_requirable = [
            self.FIELD_BOOLEAN,
            self.FIELD_RADIO_GROUP,
            self.FIELD_CHECKBOX_GROUP,
        ]
        return self.type not in not_requirable