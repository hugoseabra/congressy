# pylint: disable=W5101
"""
    Formulario personalizada a ser usado dentro do evento, principalmente
    dentro da organização.
"""


from django.db import models
from gatheros_event.models import Event
from survey.models import Survey


class EventSurvey(models.Model):
    """Modelo de formularios de evento"""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='surveys'
    )

    survey = models.OneToOneField(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='formulario',
        related_name='event',
    )
