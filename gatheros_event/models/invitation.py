from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from . import Member


class Invitation(models.Model):
    """ Convite para organização """

    DEFAULT_DAYS_FOR_EXPIRATION = 6

    INVITATION_TYPE_HELPER = 'helper'
    INVITATION_TYPE_ADMIN = 'admin'

    INVITATION_TYPES = (
        (INVITATION_TYPE_HELPER, 'Auxiliar'),
        (INVITATION_TYPE_ADMIN, 'Administrador'),
    )

    author = models.ForeignKey(Member, verbose_name='autor', on_delete=models.CASCADE)
    to = models.ForeignKey(User, verbose_name='convidado', on_delete=models.CASCADE, related_name='invitations')
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
        organization = self.author.organization
        author_user = self.author.person.user

        if organization.internal is True:
            raise IntegrityError('Organizações internas não aceitam convites')

        if Invitation.objects.filter(author=self.author, to=self.to).count() > 0:
            raise ValidationError({'to': ['Convite já foi enviado para \'%s\'' % self.to.person.name]})

        if self._is_organization_member(self.to) is True:
            raise ValidationError(
                {'to': [
                    '\'%s\' já é membro da organização \'%s\''
                    % (self.to.person.name, organization.name)
                ]}
            )

        if self._is_organization_member(author_user, Member.ADMIN) is False:
            raise ValidationError(
                {'author': [
                    'O autor \'%s\' não é membro administrador da organização \'%s\''
                    % (self.author.person.name, organization.name)
                ]}
            )

        if author_user == self.to:
            raise ValidationError(
                {'to': [
                    'O autor \'%s\' convidou a si mesmo para uma organização que ele já é membro'
                    % self.to.person.name
                ]})

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ('created', 'author',)

    def __str__(self):
        return '{} ({}) - {}'.format(self.to.first_name, self.author.organization.name, self.created)

    def _is_organization_member(self, user, group=None):
        is_member = False

        organization = self.author.organization

        if not group:
            organization_members = organization.members.all()
        else:
            organization_members = organization.members.filter(group=group)

        for member in user.person.members.all():
            if member in organization_members:
                is_member = True

        return is_member
