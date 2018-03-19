"""
    Question domain model.
    Pergunta de um Questionário, que poderá ser de diversos tipos, obrigatório
    ou não, ativo ou não.
"""
from django.db import models
from survey.models import Survey
from survey.models.mixins import Entity


class Question(Entity, models.Model):
    """
        Question domain model implementation.
    """

    class Meta:
        verbose_name = 'Pergunta de Questionario'
        verbose_name_plural = 'Perguntas de Questionario'
        unique_together = (
            ('survey', 'name',),
        )

    def __str__(self):  # pragma: no cover
        return self.name

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

    @property
    def accepts_options(self):
        """ Campos aceitos pelo formulário. """

        accepted_fields = [
            self.FIELD_SELECT,
            self.FIELD_CHECKBOX_GROUP,
            self.FIELD_RADIO_GROUP,
        ]

        if self.type in accepted_fields:
            return True

        return False
