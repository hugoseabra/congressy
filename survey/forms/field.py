from django.core.exceptions import FieldError
from django.core.validators import FileExtensionValidator
from django.forms import fields, widgets, SelectDateWidget, Media

from core.forms.widgets import DateTimeInput, TelephoneInput
from core.util.date import create_years_list


# def get_file_path(instance, filename):
#     """ Resgata localização onde as imagens serão inseridas. """
#
#     return os.path.join(
#         'survey',
#         str(instance.survey.pk),
#         str(instance.id),
#         os.path.basename(filename)
#     )


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
    FIELD_INPUT_FILE_PDF = 'input-file-pdf'
    FIELD_INPUT_PHONE = 'input-phone'
    FIELD_INPUT_PHONE_PHONE = 'input-phone-phone'
    FIELD_INPUT_PHONE_CELLPHONE = 'input-phone-cellphone'
    FIELD_INPUT_PHONE_CPF = 'input-phone-cpf'
    FIELD_INPUT_PHONE_CNPJ = 'input-phone-cnpj'
    FIELD_TEXTAREA = 'textarea'
    FIELD_BOOLEAN = 'boolean'
    FIELD_SELECT = 'select'
    FIELD_CHECKBOX_GROUP = 'checkbox-group'
    FIELD_RADIO_GROUP = 'radio-group'

    supported_types = [
        FIELD_INPUT_TEXT,
        FIELD_INPUT_PHONE_CPF,
        FIELD_INPUT_PHONE_CNPJ,
        FIELD_INPUT_FILE_PDF,
        FIELD_INPUT_PHONE_PHONE,
        FIELD_INPUT_PHONE_CELLPHONE,
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
        self.is_active = question.active
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
                label=self.label,
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

        if self.type == self.FIELD_INPUT_FILE_PDF:
            self.django_field = fields.FileField(
                max_length=500,
                label=self.label.title(),
                required=False,
                initial=self.initial,
                help_text=self.help_text,
                validators=[
                    FileExtensionValidator(allowed_extensions=['pdf']),
                ]
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

        if self.type == self.FIELD_INPUT_PHONE_CPF:
            self.django_field = fields.CharField(
                max_length=14,  # máscara será aplicada
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget(),
            )

        if self.type == self.FIELD_INPUT_PHONE_CNPJ:
            self.django_field = fields.CharField(
                max_length=18,  # máscara será aplicada
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_INPUT_PHONE_PHONE:
            self.django_field = fields.CharField(
                max_length=14,  # máscara será aplicada
                label=self.label.title(),
                required=self.required,
                initial=self.initial,
                help_text=self.help_text,
                widget=self._get_widget()
            )

        if self.type == self.FIELD_INPUT_PHONE_CELLPHONE:
            self.django_field = fields.CharField(
                max_length=15,  # máscara será aplicada
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
                required=self.required,
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
        self.django_field.is_active = self.is_active
        self.django_field.field_type = self.type
        self.django_field.question_id = self.question.pk
        self.django_field.question_name = self.question.name

        return self.django_field

    def _get_widget(self):
        """ Recupera o Widget correto de acordo com o tipo de campo. """

        widget_class = None
        widget_attrs = {}

        if self.type == self.FIELD_INPUT_TEXT:
            widget_class = widgets.TextInput

        elif self.type == self.FIELD_INPUT_NUMBER:
            widget_class = TelephoneInput
            widget_attrs = {
                'clear_string': False,
                'attrs': {
                    'onkeyup':
                        "this.value.replace(/[^0-9.]/g, '')"
                        ".replace(/(\..*)\./g, '$1');",
                    'data-field-name': 'input-number'
                }
            }

        elif self.type == self.FIELD_INPUT_DATE:
            widget_class = SelectDateWidget
            widget_attrs = {
                'attrs': {'style': 'width: 30%; display: inline-block;'},
                'years': create_years_list(),
            }

        elif self.type == self.FIELD_INPUT_DATETIME:
            widget_class = DateTimeInput
            widget_attrs = {'format': '%d/%m/%Y %H:%M:%S'}

        elif self.type == self.FIELD_INPUT_EMAIL:
            widget_class = fields.EmailInput

        elif self.type == self.FIELD_INPUT_PHONE:
            widget_class = TelephoneInput

        elif self.type == self.FIELD_INPUT_PHONE_CPF:
            widget_class = TelephoneInput
            widget_attrs = {
                'attrs': {
                    'data-mask': '###.###.###-##',
                    'data-field-name': 'input-phone-cpf',
                }
            }

        elif self.type == self.FIELD_INPUT_PHONE_CNPJ:
            widget_class = TelephoneInput
            widget_attrs = {
                'attrs': {
                    'data-mask': '##.###.###/####-##',
                    'data-field-name': 'input-phone-cnpj',
                }
            }

        elif self.type == self.FIELD_INPUT_PHONE_PHONE:
            widget_class = TelephoneInput
            widget_attrs = {
                'attrs': {
                    'data-mask': '(##) ####-####',
                    'data-mask-name': 'phone',
                }

            }

        elif self.type == self.FIELD_INPUT_PHONE_CELLPHONE:
            widget_class = TelephoneInput
            widget_attrs = {
                'attrs': {
                    'data-mask': '(##) #####-####',
                    'data-mask-name': 'cellphone',
                }
            }

        elif self.type == self.FIELD_BOOLEAN:
            widget_class = widgets.CheckboxInput

        elif self.type == self.FIELD_SELECT:
            widget_class = widgets.Select

            if self.select_intro:
                intro_option = [('', '- Selecione -',)]
                self.options = intro_option + self.options

        elif self.type == self.FIELD_TEXTAREA:
            widget_class = widgets.Textarea

        elif self.type == self.FIELD_RADIO_GROUP:
            widget_class = widgets.RadioSelect

        elif self.type == self.FIELD_CHECKBOX_GROUP:
            widget_class = widgets.CheckboxSelectMultiple

        if not widget_class or not issubclass(widget_class, widgets.Widget):
            raise Exception('Field type not supported: {}'.format(self.type))

        def _media(self):
            return Media(js=(
                'assets/survey/js/plugins/mask/mask.min.js',
                'assets/survey/js/predefined-fields.js',
            ))

        widget_class.media = property(_media)
        return self._configure_widget(widget_class, **widget_attrs)

    def _configure_widget(self, widget_class, **kwargs):
        """ Configura widget inserindo parâmetros necessários. """

        attrs = kwargs.get('attrs', {})
        attrs.update(self.attrs)

        if self.has_requirement() and self.required:
            attrs.update({
                'required': self.required
            })

        if self.placeholder:
            attrs.update({
                'placeholder': self.placeholder
            })

        kwargs.update({'attrs': attrs})
        return widget_class(**kwargs)

    def has_requirement(self):
        """ Verifica se campos possuem atributo `required`. """
        not_requirable = [
            self.FIELD_BOOLEAN,
            self.FIELD_RADIO_GROUP,
            self.FIELD_CHECKBOX_GROUP,
        ]
        return self.type not in not_requirable
