from django.db import models
from django.contrib.auth.models import User
from . import Organization


class Invitation(models.Model):
    """ Convite para organização """

    INVITATION_TYPES = (
        ('helper', 'Auxiliar'),
        ('admin', 'Administrador'),
    )

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='organização',
                                     related_name='invitations')
    to = models.ForeignKey(User, verbose_name='convidado', on_delete=models.CASCADE, related_name='invitations')
    author = models.ForeignKey(User, verbose_name='autor', on_delete=models.CASCADE)
    created = models.DateField(verbose_name='criado em', auto_created=True)
    expired = models.DateField(verbose_name='expira em', blank=True, null=True)
    type = models.CharField(max_length=10, choices=INVITATION_TYPES, verbose_name='tipo', default='helper')

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ('created',)

    def __str__(self):
        return '{} ({}) - {}'.format(self.to.first_name, self.organization.name, self.created)
