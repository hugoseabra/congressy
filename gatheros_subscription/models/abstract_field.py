# pylint: disable=W5101
"""
Classe abstrata para Campo de formulário
"""

from django.db import models

from gatheros_event.models.mixins import GatherosModelMixin


class AbstractField(models.Model, GatherosModelMixin):
    """ Campo de formulário. """

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

    TYPES = (
        (FIELD_INPUT_TEXT, 'Texto (255 caracteres)'),
        (FIELD_INPUT_NUMBER, 'Número'),
        (FIELD_INPUT_DATE, 'Data'),
        (FIELD_INPUT_DATETIME, 'Data e hora'),
        (FIELD_INPUT_EMAIL, 'E-mail'),
        (FIELD_INPUT_PHONE, 'Telefone'),
        (FIELD_TEXTAREA, 'Texto longo'),
        (FIELD_BOOLEAN, 'SIM/NÃO'),
        (FIELD_SELECT, 'Lista simples'),
        (FIELD_CHECKBOX_GROUP, 'Múltipla escolha'),
        (FIELD_RADIO_GROUP, 'Escolha única'),
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
        blank=True
    )
    label = models.CharField(
        max_length=255,
        verbose_name='rótulo'
    )
    field_type = models.CharField(
        max_length=20,
        choices=TYPES,
        default='input-text',
        verbose_name='tipo'
    )
    required = models.BooleanField(
        default=False,
        verbose_name='obrigatório'
    )
    select_intro = models.BooleanField(
        default=False,
        verbose_name='Mostrar primeiro em branco',
        help_text="Acrescenta `- Selecione -` na primeira opção da lista"
                  " simples"
    )
    instruction = models.TextField(
        verbose_name='instrução',
        null=True,
        blank=True
    )
    placeholder = models.CharField(
        max_length=100,
        verbose_name='placeholder',
        null=True,
        blank=True
    )
    default_value = models.TextField(
        verbose_name='valor padrão',
        null=True,
        blank=True
    )
    with_options = models.BooleanField(
        default=False,
        verbose_name='possui opções'
    )
    active = models.BooleanField(default=True, verbose_name='ativo')

    class Meta:
        abstract = True

    def save(self, **kwargs):
        """ Salva entidade. """
        self._accepts_options()
        return super(AbstractField, self).save(**kwargs)

    def _accepts_options(self):
        """ Campos aceitos pelo formulário. """
        self.with_options = self.field_type in [
            self.FIELD_SELECT,
            self.FIELD_CHECKBOX_GROUP,
            self.FIELD_RADIO_GROUP,
        ]
