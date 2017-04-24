from django.db import IntegrityError, models

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
    invitation_accepted = models.BooleanField(default=False, verbose_name='convite aceito')
    active = models.BooleanField(default=True, verbose_name='ativo')

    def __str__(self):
        return '{} ({})'.format(self.person.name, self.organization.name)

    class Meta:
        verbose_name = 'membro'
        verbose_name_plural = 'membros'
        ordering = ['person', 'organization']

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Member, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._check_remove_if_internal_organization_member()
        super(Member, self).delete(*args, **kwargs)

    def clean(self):
        self._configure_if_internal()

        if self.person.user is None:
            raise IntegrityError('Pessoas sem vínculo com usuários não podem ser participar de organizações')

    def _configure_if_internal(self):
        if not self.organization.internal:
            return

        if self not in self.organization.members.all() and self.organization.members.count() > 0:
            raise IntegrityError('Organizações internas não podem ter membros')

        if self.group == self.HELPER:
            raise IntegrityError('Membro de organização interna não pode ser \'%s\'' % self.get_group_display())

    def _check_remove_if_internal_organization_member(self):
        if self.organization.internal is True:
            raise IntegrityError(
                'Impossível remover membro. Organização interna deve possuir um membro ADMIN principal.'
            )
