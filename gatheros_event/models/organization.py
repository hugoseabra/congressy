from django.contrib.auth.models import User
from django.db import models

from core.util import slugify
from .member import Member
from .person import Person


class Organization(models.Model):
    """ Organização """
    name = models.CharField(max_length=100, verbose_name='nome')
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='descrição'
    )
    slug = models.SlugField(
        max_length=128,
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
        verbose_name='foto'
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
        verbose_name='gerado internamente'
    )

    class Meta:
        verbose_name = 'organização'
        verbose_name_plural = 'organizações'
        ordering = ['name']

        permissions = (
            ("can_invite", "Can invite members"),
            ("can_view", "Can view"),
            ("can_add_event", "Can add event"),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self._create_unique_slug()
        super(Organization, self).save(*args, **kwargs)

    def _create_unique_slug(self):
        self.slug = slugify(
            model_class=Organization,
            slugify_from=self.name,
            primary_key=self.pk
        )

    def get_members(self, group=None, person=None):
        qs = self.members.all()

        if group:
            qs = qs.filter(group=group)

        if person:
            if isinstance(person, User):
                person = Person.objects.get(user=person)

            qs = qs.filter(person=person)

        return qs

    def is_member(self, person):
        """
        Verifica se a pessoa ou usuário é membro da organização

        :param person: Pessoa ou usuário que é membro
        :return:
        """
        if isinstance(person, User):
            person = Person.objects.get(user=person)

        return self.get_members(person=person).exists()

    def is_admin(self, person):
        """
        Verifica se a pessoa ou usuário é administrador da organização

        :param person: Pessoa ou usuário que é membro
        :return:
        """
        if isinstance(person, User):
            person = Person.objects.get(user=person)

        return self.get_members(group=Member.ADMIN, person=person).exists()
