import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models

from core.model import track_data
from gatheros_event import settings
from . import Member
from .rules import check_invite


@track_data('author', 'to')
class Invitation(models.Model):
    """ Convite para organização """

    INVITATION_TYPE_HELPER = 'helper'
    INVITATION_TYPE_ADMIN = 'admin'

    INVITATION_TYPES = (
        (INVITATION_TYPE_HELPER, 'Auxiliar'),
        (INVITATION_TYPE_ADMIN, 'Administrador'),
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    author = models.ForeignKey(
        Member,
        verbose_name='autor',
        on_delete=models.CASCADE
    )
    to = models.ForeignKey(
        User,
        verbose_name='convidado',
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    created = models.DateTimeField(verbose_name='criado em')
    expired = models.DateTimeField(
        verbose_name='expira em',
        blank=True,
        null=True
    )
    type = models.CharField(
        max_length=10,
        choices=INVITATION_TYPES,
        verbose_name='tipo',
        default='helper'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.created = datetime.now()
            self.expired = self.created + timedelta(
                days=settings.INVITATION_ACCEPT_DAYS
            )

        self.full_clean()
        super(Invitation, self).save(*args, **kwargs)

    def clean(self):
        check_invite(self)

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ('created', 'author',)
        unique_together = (('author', 'to'),)

    def __str__(self):
        return '{} - {}'.format(
            self.author.organization.name,
            self.to.first_name if self.to.first_name else self.to.email
        )

    def has_previous(self):
        return Invitation.objects.filter(
            author__organization=self.author.organization, to=self.to).exists()
