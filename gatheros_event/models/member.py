# pylint: disable=W5101
"""
Membro de organização, pertencente a um determinado grupo, responsável para
gerir as informações relacionadas aos eventos da organização.
"""

from django.db import models

from gatheros_event.models.rules import member as rule
from . import Person


class Member(models.Model):
    """Membro de organização."""

    ADMIN = 'admin'
    HELPER = 'helper'

    GROUP_CHOICES = (
        (ADMIN, 'Administrador'),
        (HELPER, 'Auxiliar'),
    )

    organization = models.ForeignKey(
        'gatheros_event.Organization',
        on_delete=models.CASCADE,
        verbose_name='organização',
        related_name='members'
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name='pessoa',
        related_name='members'
    )
    group = models.CharField(
        max_length=20,
        choices=GROUP_CHOICES,
        verbose_name='grupo'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )
    active = models.BooleanField(default=True, verbose_name='ativo')

    def __str__(self):
        return '{} ({})'.format(self.person.name, self.organization.name)

    class Meta:
        verbose_name = 'membro'
        verbose_name_plural = 'membros'
        ordering = ['person', 'organization']

    def save(self, *args, **kwargs):
        self.check_rules()
        super(Member, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        rule.rule_4_nao_remover_member_organizacao_interna(self)
        super(Member, self).delete(*args, **kwargs)

    def check_rules(self):
        """Verifica regras de Membro"""
        rule.rule_1_membros_deve_ter_usuarios(self)
        rule.rule_2_organizacao_interna_apenas_1_membro(
            self,
            self._state.adding
        )
        rule.rule_3_organizacao_interna_unico_membro_admin(
            self,
            self._state.adding
        )

    def is_admin(self):
        """ Verifica se membro é administrador """
        return self.group == Member.ADMIN
