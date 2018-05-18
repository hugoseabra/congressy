from django.db import models
from gatheros_event.models import Event


class WorkConfig(models.Model):

    ORAL = 'oral'
    POSTER = 'poster'
    ORAL_AND_POSTER = 'oral e poster'

    PRESENTING_TYPES = (
        (ORAL, 'Oral'),
        (POSTER, 'Poster'),
        (ORAL_AND_POSTER, 'Oral e Poster'),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="submission_configs",
    )

    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final')

    presenting_type = models.CharField(
        max_length=25,
        verbose_name="tipos de apresentações",
        choices=PRESENTING_TYPES,
        default=ORAL,
    )

    def __str__(self):
        return "Configurações cientificas do " + self.event.name

