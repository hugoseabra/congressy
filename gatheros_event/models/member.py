from datetime import datetime

from django.db import models

from gatheros_event.models.rules import member as rule
from . import Organization, Person


class Member(models.Model):
    ADMIN = 'admin'
    HELPER = 'helper'

    GROUP_CHOICES = (
        (ADMIN, 'Administrador'),
        (HELPER, 'Auxiliar'),
    )

    organization = models.ForeignKey(Organization, verbose_name='organização', related_name='members')
    person = models.ForeignKey(Person, verbose_name='pessoa', related_name='members')
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, verbose_name='grupo')
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    created_by = models.PositiveIntegerField(verbose_name='criado por')  # ID do usuário
    invited_on = models.DateTimeField(auto_now_add=True, verbose_name='convidado em')
    accepted = models.BooleanField(default=False, verbose_name='convite aceito')
    accepted_on = models.DateTimeField(null=True, blank=True, verbose_name='aceito em')
    active = models.BooleanField(default=True, verbose_name='ativo')

    def __str__(self):
        return '{} ({})'.format(self.person.name, self.organization.name)

    class Meta:
        verbose_name = 'membro'
        verbose_name_plural = 'membros'
        ordering = ['person', 'organization']

    def save(self, *args, **kwargs):
        if self.accepted:
            self.accepted_on = datetime.now()

        self.full_clean()
        super(Member, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        rule.rule_4_nao_remover_member_organizacao_interna(self)
        super(Member, self).delete(*args, **kwargs)

    def clean(self):
        rule.rule_1_membros_deve_ter_usuarios(self)
        rule.rule_2_organizacao_interna_apenas_1_membro(self, self._state.adding)
        rule.rule_3_organizacao_interna_unico_membro_admin(self, self._state.adding)
