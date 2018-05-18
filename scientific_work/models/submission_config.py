from django.db import models
from gatheros_event.models import Event


class SubmissionConfig(models.Model):

    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final')

    allow_submissions = models.BooleanField(
        default=False,
        verbose_name="permitir submissões"
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="submission_configs",
    )

    def __str__(self):
        return "Configurações cientificas do " + self.event.name

