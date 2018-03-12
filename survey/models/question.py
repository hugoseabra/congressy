"""
    Question domain model.
"""
from django.db import models
from survey.models import Survey


class Question(models.Model):
    """
        Question domain model implementation.
    """

    class Meta:
        verbose_name = 'Pergunta de Questionario'
        verbose_name_plural = 'Perguntas de Questionario'
        unique_together = (
            ('survey', 'name',),
        )

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

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='questionario',
        related_name='questions',
    )

    type = models.CharField(
        max_length=50,
        choices=TYPES,
        verbose_name='tipo'
    )

    name = models.CharField(
        max_length=255,
        verbose_name='titulo',
    )

    label = models.CharField(
        max_length=255,
        verbose_name='rotulo'
    )

    required = models.BooleanField(
        default=False,
        verbose_name='obrigatoriedade',
    )

    help_text = models.CharField(
        max_length=255,
        verbose_name='texto de ajuda',
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        default=True,
        verbose_name='ativo'
    )

    @property
    def has_options(self):
        return self.options.count() > 0

    def _accepts_options(self):
        """ Campos aceitos pelo formulário. """
        self.with_options = self.field_type in [
            self.FIELD_SELECT,
            self.FIELD_CHECKBOX_GROUP,
            self.FIELD_RADIO_GROUP,
        ]
