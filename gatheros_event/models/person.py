# pylint: disable=W5101,E0401,C0103
"""
Pessoa, nesta aplicação, é o principal objetivo de toda a plataforma, que
serão os usuários e/ou participantes de eventos na plataforma.
"""
import uuid
from datetime import date

from django.contrib.auth.models import User
from django.db import models

from core.model import track_data
from core.model.validator import cpf_validator, phone_validator
from kanu_locations.models import City
from . import Occupation
from .mixins import GatherosModelMixin


@track_data('name', 'user', 'email')
class Person(models.Model, GatherosModelMixin):
    """Pessoa"""

    RESOURCE_URI = '/api/core/people/'

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Masculino'),
        (GENDER_FEMALE, 'Feminino'),
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    name = models.CharField(max_length=255, verbose_name='nome')
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name='sexo',
        blank=False,
        null=False,
        default=GENDER_MALE
    )
    email = models.EmailField(
        verbose_name='e-mail',
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='cidade'
    )
    zip_code = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        verbose_name='CEP'
    )
    street = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='logradouro',
        help_text="Rua / Avenida / Viela / etc."
    )
    number = models.CharField(
        max_length=20,
        verbose_name='número',
        blank=True,
        null=True,
        help_text="Caso não tenha, informar S/N."
    )
    complement = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='complemento'
    )
    village = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='bairro'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='celular',
        validators=[phone_validator]
    )

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='usuário',
        related_name='person'
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        verbose_name='foto',
        upload_to='person',
    )
    cpf = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='CPF',
        validators=[cpf_validator]
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='data de nasc.'
    )
    rg = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='rg'
    )
    orgao_expedidor = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='orgão expedidor'
    )
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    synchronized = models.NullBooleanField(default=False)
    term_version = models.IntegerField(
        verbose_name='versão do termo de uso',
        blank=True,
        null=True
    )
    politics_version = models.IntegerField(
        verbose_name='versão da política de privacidade',
        blank=True,
        null=True
    )
    occupation = models.ForeignKey(
        Occupation,
        on_delete=models.SET_NULL,
        verbose_name='profissão',
        blank=True,
        null=True
    )
    pne = models.BooleanField(
        verbose_name='portador de necessidades especiais',
        default=False
    )

    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)

    @property
    def age(self):
        if not self.birth_date:
            return None

        current = date.today()

        was_earlier = (current.month, current.day) < \
                      (self.birth_date.month, self.birth_date.day)
        return current.year - self.birth_date.year - was_earlier

    class Meta:
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = None

        if not self.cpf:
            self.cpf = None

        self.full_clean()
        super(Person, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Usuário permamancerá no sistema pois pode haver registros ligados
        """
        if self.user and self.user.is_active is True:
            self.user.is_active = False
            self.user.save()

        super(Person, self).delete(*args, **kwargs)

    def get_cpf_display(self):
        """
        Recupera CPF formatado.

        :return: string
        """
        cpf = str(self.cpf)
        if not cpf:
            return ''
        return '{0}.{1}.{2}-{3}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:11])

    def get_birth_date_display(self):
        """
        Recupera data de nascimento formatada.
        :return: string
        """
        if not self.birth_date:
            return '--'
        return self.birth_date.strftime('%d/%m/%Y')

    def get_profile_data(self):
        """ Resgata dados a serem utilizados publicamente no perfil. """
        return {
            'avatar': self.avatar,
            'name': self.name,
            'website': self.website,
            'facebook': self.facebook,
            'twitter': self.twitter,
            'linkedin': self.linkedin,
            'skype': self.skype,
        }
