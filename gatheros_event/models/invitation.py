# pylint: disable=W5101,C0103
"""
Convite para que uma pessoa, cadastrada ou não, possa participar de uma
organização.
"""

import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models

from core.model import track_data
from gatheros_event import settings
from . import Member
from .mixins import GatherosModelMixin
from .rules import check_invite


class InvitationManager(models.Manager):
    """ Manager - Gerenciador de Convites. """
    def get_invitations(self, organization):
        return self.filter(organization=organization).all


@track_data('author', 'to')
class Invitation(models.Model, GatherosModelMixin):
    """ Convite para organização """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    author = models.ForeignKey(
        Member,
        verbose_name='autor',
        on_delete=models.CASCADE,
        related_name='invitations'
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
    group = models.CharField(
        max_length=10,
        choices=Member.GROUP_CHOICES,
        verbose_name='grupo',
        default=Member.HELPER
    )

    objects = InvitationManager()

    @property
    def is_expired(self):
        """ Verifica se convite já está expirado. """
        return self.expired < datetime.now()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._set_dates()

        self.full_clean()
        super(Invitation, self).save(*args, **kwargs)

    def clean(self):
        check_invite(self)

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ('-created', '-expired', 'author',)
        unique_together = (('author', 'to'),)

    def __str__(self):
        return '{} - {}'.format(
            self.author.organization.name,
            self.to.first_name if self.to.first_name else self.to.email
        )

    def _set_dates(self):
        self.created = datetime.now()
        self.expired = self.created + timedelta(
            days=settings.INVITATION_ACCEPT_DAYS
        )

    def has_previous(self):
        """
        Verifica se existe convite prévio.
        :return: bool
        """
        return Invitation.objects.filter(
            author__organization=self.author.organization, to=self.to).exists()

    def renew(self, save=False):
        """ Renova convite. """

        self._set_dates()

        if save:
            self.save()
