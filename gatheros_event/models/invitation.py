from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

from . import Organization


class Invitation(models.Model):
    """ Convite para organização """

    DEFAULT_DAYS_FOR_EXPIRATION = 6

    INVITATION_TYPES = (
        ('helper', 'Auxiliar'),
        ('admin', 'Administrador'),
    )

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='organização',
                                     related_name='invitations')
    to = models.ForeignKey(User, verbose_name='convidado', on_delete=models.CASCADE, related_name='invitations')
    author = models.ForeignKey(User, verbose_name='autor', on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='criado em')
    expired = models.DateTimeField(verbose_name='expira em', blank=True, null=True)
    type = models.CharField(max_length=10, choices=INVITATION_TYPES, verbose_name='tipo', default='helper')

    def save(self, *args, **kwargs):

        if self._state.adding:
            self.created = datetime.now()
            self.expired = self.created + timedelta(days=self.DEFAULT_DAYS_FOR_EXPIRATION)

        self.full_clean()
        super(Invitation, self).save(*args, **kwargs)

    def clean(self):
        if self.author == self.to:
            raise ValidationError({'to': ['Autor não pode convidar a se mesmo para organização que ele já é membro.']})

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ('created', 'organization',)

    def __str__(self):
        return '{} ({}) - {}'.format(self.to.first_name, self.organization.name, self.created)
