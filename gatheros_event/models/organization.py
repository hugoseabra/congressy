# pylint: disable=W5101
"""
Organização é a estrutura máxima da aplicação, pois nela, define-se seus
membros, com seus devidos grupos, e como eles poderão interagir nos eventos
vinculadas a ela.
"""
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.html import strip_tags
from core.util import model_field_slugify
from .member import Member
from .mixins import GatherosModelMixin
from .person import Person


class Organization(models.Model, GatherosModelMixin):
    """ Organização """
    name = models.CharField(max_length=100, verbose_name='nome')
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='descrição (texto)'
    )
    description_html = models.TextField(
        null=True,
        blank=True,
        verbose_name='descrição (HTML)'
    )
    slug = models.SlugField(
        max_length=128,
        blank=True,
        null=True,
        unique=True,
        verbose_name='permalink',
        help_text="Link que aparecerá para exibir as informações da"
                  " organizações: https://gatheros.com/<permalink>"
    )

    avatar_width = models.PositiveIntegerField(null=True, blank=True)
    avatar_height = models.PositiveIntegerField(null=True, blank=True)
    avatar = models.ImageField(
        blank=True,
        null=True,
        width_field='avatar_width',
        height_field='avatar_height',
        verbose_name='foto',
        upload_to='organization',
    )
    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)

    cash_provider = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='provedor de recebimento'
    )
    cash_data = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='dados para recebimento'
    )
    active = models.BooleanField(default=True, verbose_name='ativo')
    internal = models.BooleanField(
        default=True,
        verbose_name='interno'
    )

    class Meta:
        verbose_name = 'organização'
        verbose_name_plural = 'organizações'
        ordering = ['name']

        permissions = (
            ("can_invite", "Can invite members"),
            ("can_view", "Can view"),
            ("can_add_event", "Can add event"),
            ("can_view_members", "Can view members"),
            ("can_manage_members", "Can manage members"),
            ("can_manage_places", "Can manage places"),
            ("can_manage_fields", "Can manage form fields"),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Salva entidade. """
        self._create_unique_slug()
        self.description = strip_tags(self.description_html)
        super(Organization, self).save(*args, **kwargs)

    def _create_unique_slug(self):
        self.slug = model_field_slugify(
            model_class=self.__class__,
            instance=self,
            string=self.name
        )

    def get_members(self, group=None, person=None):
        """
        Recupera litsa de membros.

        :param group: string - Filtro de lista por grupo
        :param person: object - filtro de lista por Instância de Person ou User
        :return: QuerySet
        """
        qs = self.members.all()

        if group:
            qs = qs.filter(group=group)

        if person:
            if isinstance(person, User):
                try:
                    person = Person.objects.get(user=person)
                except Person.DoesNotExist:
                    return []

            qs = qs.filter(person=person)
        return qs

    def get_member(self, person):
        """ Recupera Member de organização. """
        members_qs = self.get_members(person=person)
        if len(members_qs) == 0:
            return None

        return members_qs.first()

    def is_member(self, person):
        """
        Verifica se a pessoa ou usuário é membro da organização

        :param person: Pessoa ou usuário que é membro
        :return:
        """
        return len(self.get_members(person=person)) > 0

    def is_admin(self, person):
        """
        Verifica se a pessoa ou usuário é administrador da organização

        :param person: Pessoa ou usuário que é membro
        :return:
        """
        return len(self.get_members(group=Member.ADMIN, person=person)) > 0

    def is_member_active(self, person):
        """ Verifica se membro está ativo na organização. """
        member = self.get_member(person)
        return member.active if member else False

    def get_invitations(self, include_expired=True, limit=None):
        """
        Recupera convites da organização feita por membros administradores
        """
        invitations = []
        for member in self.members.all():
            invitation_qs = member.invitations
            if not include_expired:
                now = datetime.now()
                invitation_qs = invitation_qs.filter(expired__gte=now)

            if limit:
                invitations += list(invitation_qs.all()[0:int(limit)])
            else:
                invitations += list(invitation_qs.all())

        return invitations
