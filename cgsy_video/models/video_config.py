import uuid
from django.db import models


class VideoConfig(models.Model):
    class Meta:
        verbose_name = 'Configuração de vídeo'
        verbose_name_plural = 'Configurações de vídeo'

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    event = models.OneToOneField(
        to='gatheros_event.Event',
        verbose_name='event',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='video_config',
    )

    token = models.CharField(
        max_length=64,
        verbose_name='token',
        null=False,
        blank=False,
    )

    project_pk = models.UUIDField(
        verbose_name='project pk',
        null=False,
        blank=False,
    )
