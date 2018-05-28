from datetime import datetime

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

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="work_config",
    )

    date_start = models.DateTimeField(
        verbose_name='data inicial',
        blank=True,
        null=True,
    )
    date_end = models.DateTimeField(
        verbose_name='data final',
        blank=True,
        null=True,
    )

    presenting_type = models.CharField(
        max_length=25,
        verbose_name="tipos de apresentações",
        choices=PRESENTING_TYPES,
        default=ORAL,
        blank=True,
        null=True,
    )

    @property
    def is_submittable(self):
        now = datetime.now()
        area_categories = self.event.area_categories.all()
        if self.date_start <= now <= self.date_end \
                and area_categories.count() > 0:
            return True

        return False

    def __str__(self):
        return "Configurações cientificas do " + self.event.name
