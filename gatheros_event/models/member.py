from django.db import models
from . import Organization, Person


class Member(models.Model):
    GROUP_CHOICES = (
        ('admin', 'Administrador'),
        ('helper', 'Auxiliar'),
    )

    person = models.ForeignKey(Person, verbose_name='pessoa')
    organization = models.ForeignKey(Organization, verbose_name='organização')
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, verbose_name='grupo')
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    created_by = models.PositiveIntegerField(verbose_name='criado por')  # ID do usuário
    invited_on = models.DateTimeField(verbose_name='convidado em')
    invitation_accepted = models.BooleanField(default=False, verbose_name='convite aceito')
    active = models.BooleanField(default=True, verbose_name='ativo')

    def __str__(self):
        return '{} ({})'.format(self.person.name, self.organization.name)

    class Meta:
        verbose_name = 'membro'
        verbose_name_plural = 'membros'
        ordering = ['person', 'organization']
