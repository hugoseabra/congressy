import uuid

from django.db import models


class MailChimpIntegration(models.Model):
    class Meta:
        verbose_name = 'MailChimp Integração'
        verbose_name_plural = 'MailChimp Integrações'

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    event = models.OneToOneField(
        to='gatheros_event.Event',
        verbose_name='event',
        related_name='mailchimp_integration',
        null=False,
        blank=False,
    )

    api_key = models.CharField(
        max_length=48,
        verbose_name='Chave da API',
        help_text='Encontre a chave de API do Mailchimp e cole aqui',
        null=False,
        blank=False,
    )

    default_tag = models.CharField(
        max_length=48,
        verbose_name='Tag padrão',
        help_text='Tag para identificar o participante como membro da lista',
        null=False,
        blank=False,
    )

    list_id = models.CharField(
        max_length=48,
        verbose_name='ID da Lista de Audiência',
        help_text='ID da Lista de Audiência',
        null=True,
        blank=True,
    )

    sync_phone = models.BooleanField(
        verbose_name='Sincronizar Telefone',
        default=True,
        null=False,
        blank=False,
    )

    sync_address = models.BooleanField(
        verbose_name='Sincronizar endereço',
        default=True,
        null=False,
        blank=False,
    )
