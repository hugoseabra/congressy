from datetime import datetime

from django.db import models

from gatheros_event.models import Event


class WorkConfig(models.Model):

    class Meta:
        verbose_name = 'Configuração de Submissão'
        verbose_name_plural = 'Configurações de Submissões'

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

    allow_unconfirmed_subscriptions = models.BooleanField(
        default=False,
        verbose_name="permitir inscrições não confirmadas",
    )

    @property
    def is_configured(self):
        area_categories = self.event.area_categories.all()

        if not self.date_start or not self.date_end:
            return False

        if not area_categories.count() > 0:
            return False

        return True

    @property
    def is_submittable(self):
        now = datetime.now()
        running = False

        if self.date_start and self.date_end:
            running = self.date_end > now > self.date_start

        return self.is_configured and running

    def __str__(self):
        return "Configurações cientificas do " + self.event.name
