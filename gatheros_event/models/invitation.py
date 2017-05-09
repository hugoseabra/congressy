from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models

from core.model import track_data
from . import Member
from .rules import invitation as rule


@track_data('author', 'to')
class Invitation(models.Model):
    """ Convite para organização """

    DEFAULT_DAYS_FOR_EXPIRATION = 6

    INVITATION_TYPE_HELPER = 'helper'
    INVITATION_TYPE_ADMIN = 'admin'

    INVITATION_TYPES = (
        (INVITATION_TYPE_HELPER, 'Auxiliar'),
        (INVITATION_TYPE_ADMIN, 'Administrador'),
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
                days=self.DEFAULT_DAYS_FOR_EXPIRATION)

        self.check_rules()
        super(Invitation, self).save(*args, **kwargs)

    def check_rules(self):
        rule.rule_1_organizacao_internas_nao_pode_ter_convites(self)
        rule.rule_2_nao_pode_mudar_autor(self)
        rule.rule_3_nao_pode_mudar_convidado(self)
        rule.rule_4_autor_convida_a_si_mesmo(self)
        rule.rule_5_convite_ja_existente(self, self._state.adding)
        rule.rule_6_autor_deve_ser_membro_admin(self, self._state.adding)
        rule.rule_7_convidado_ja_membro_da_organizacao(self, self._state.adding)

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ('created', 'author',)
        unique_together = (('author', 'to'),)

    def validate_unique(self, exclude=None):
        super(Invitation, self).validate_unique(exclude=exclude)

    def __str__(self):
        return '{} ({}) - {}'.format(self.to.first_name,
                                     self.author.organization.name,
                                     self.created)

    def has_previous(self):
        return Invitation.objects.filter(
            author__organization=self.author.organization, to=self.to).exists()
