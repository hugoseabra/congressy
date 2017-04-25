from django.db import models
from . import Form


class FieldManager(models.Manager):
    def append_field(self, field):
        last_field = Field.objects.filter(form=field.form).order_by('-order').first()
        if last_field:
            return int(last_field.order) + 1
        else:
            return 1


class Field(models.Model):

    FIELD_INPUT_TEXT = 'input-text'
    FIELD_INPUT_DATE = 'input-date'
    FIELD_INPUT_EMAIL = 'input-email'
    FIELD_INPUT_PHONE = 'input-phone'
    FIELD_BOOLEAN = 'boolean'
    FIELD_SELECT = 'select'
    FIELD_SELECT_MULTIPLE = 'select-multiple'
    FIELD_CHECKBOX_GROUP = 'checkbox-group'
    FIELD_RADIO_GROUP = 'radio-group'

    TYPES = (
        (FIELD_INPUT_TEXT, 'INPUT-TEXT'),
        (FIELD_INPUT_DATE, 'INPUT-DATE'),
        (FIELD_INPUT_EMAIL, 'INPUT-EMAIL'),
        (FIELD_INPUT_PHONE, 'INPUT-PHONE'),
        (FIELD_BOOLEAN, 'SIM/NÃO'),
        (FIELD_SELECT, 'SELECT'),
        (FIELD_SELECT_MULTIPLE, 'SELECT-MULTIPLE'),
        (FIELD_CHECKBOX_GROUP, 'CHECKBOX-GROUP'),
        (FIELD_RADIO_GROUP, 'RADIO-GROUP'),
    )

    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name='formulário', related_name='fields')
    name = models.CharField(max_length=255, verbose_name='nome')
    label = models.CharField(max_length=255, verbose_name='rótulo')
    type = models.CharField(max_length=20, choices=TYPES, default='input-text', verbose_name='tipo')
    order = models.PositiveIntegerField(verbose_name='ordem', null=True, blank=True)

    form_default_field = models.BooleanField(default=False, verbose_name='campo fixo')
    required = models.BooleanField(default=False, verbose_name='obrigatório')
    instruction = models.TextField(verbose_name='instrução', null=True, blank=True)
    placeholder = models.CharField(max_length=100, verbose_name='placeholder', null=True, blank=True)
    default_value = models.TextField(verbose_name='valor padrão', null=True, blank=True)

    objects = FieldManager()

    class Meta:
        verbose_name = 'Campo de Formulário'
        verbose_name_plural = 'Campos de Formulário'
        ordering = ['form__id', 'order', 'name']

    def save(self, **kwargs):
        if self._state.adding and self.order is None:
            self.order = Field.objects.append_field(self)

        return super(Field, self).save(**kwargs)

    def __str__(self):
        return '{} ({})'.format(self.label, self.form)

    @property
    def options(self):
        return self.options.all()
