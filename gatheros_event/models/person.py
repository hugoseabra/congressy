import uuid

from django import forms
from django.db import models
from django.contrib.auth.models import User
from kanu_locations.models import City
from . import Occupation


class TextFieldWithInputText(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({"widget": forms.TextInput})
        return super(TextFieldWithInputText, self).formfield(**kwargs)


class Person(models.Model):
    RESOURCE_URI = '/api/core/people/'

    RECORD_TYPE = (
        ('participant', 'Participante'),
        ('event_helper', 'Auxiliar de evento'),
        ('event_manager', 'Realizador de evento'),
    )

    GENDER_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    )
    FORM_FIELDS = [
        'name',
        'genre',
        'birth_date',
        'education',
        'cpf',
        'rg',
        'orgao_expedidor',
        'city',
        'zip_code',
        'street',
        'village',
        'email',
        'phone',
        'occupation',
        'website'
        'facebook'
        'twitter'
        'linkedin'
        'skype'
        'term_version'
        'politics_version'
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = TextFieldWithInputText(verbose_name='nome')
    genre = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='sexo')

    city = models.ForeignKey(City, null=True, verbose_name='cidade')
    zip_code = models.CharField(max_length=8, blank=True, null=True, verbose_name='CEP')
    street = TextFieldWithInputText(blank=True, null=True, verbose_name='endereço')
    village = TextFieldWithInputText(blank=True, null=True, verbose_name='bairro')
    email = TextFieldWithInputText(blank=True, null=True, verbose_name='email')
    phone = TextFieldWithInputText(blank=True, null=True, verbose_name='telefone')

    record_type = models.CharField(max_length=25, choices=RECORD_TYPE, verbose_name='tipo de registro', blank=True,
                                   null=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, blank=True, null=True, verbose_name='usuário')
    avatar = models.ImageField(blank=True, null=True, verbose_name='foto')
    cpf = models.CharField(max_length=11, blank=True, null=True, verbose_name='CPF')
    birth_date = models.DateField(blank=True, null=True, verbose_name='data nascimento')
    rg = TextFieldWithInputText(blank=True, null=True, verbose_name='rg')
    orgao_expedidor = TextFieldWithInputText(blank=True, null=True, verbose_name='orgão expedidor')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    synchronized = models.NullBooleanField(default=False)
    term_version = models.IntegerField(verbose_name='versão do termo de uso', blank=True, null=True)
    politics_version = models.IntegerField(verbose_name='versão da política de privacidade', blank=True, null=True)
    occupation = models.ForeignKey(Occupation, verbose_name='profissão', blank=True, null=True)

    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    def get_cpf_display(self):
        cpf = str(self.cpf)
        if not cpf:
            return ''
        return '{0}.{1}.{2}-{3}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:11])

    def get_birth_date_display(self):
        if not self.birth_date:
            return '--'
        return self.birth_date.strftime('%d/%m/%Y')
