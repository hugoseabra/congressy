import uuid

from django import forms
from django.contrib.auth.models import User
from django.db import models
from kanu_locations.models import City

from . import Occupation
from .rules import person as rule
from ..lib.validators import cpf_validator, phone_validator
from ..lib.model import track_data


class TextFieldWithInputText(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({"widget": forms.TextInput})
        return super(TextFieldWithInputText, self).formfield(**kwargs)


@track_data('name', 'has_user', 'user', 'email')
class Person(models.Model):
    RESOURCE_URI = '/api/core/people/'

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
    name = models.CharField(max_length=255, verbose_name='nome')
    genre = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='sexo')

    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='email')

    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, verbose_name='cidade')
    zip_code = models.CharField(max_length=8, blank=True, null=True, verbose_name='CEP')
    street = TextFieldWithInputText(blank=True, null=True, verbose_name='endereço')
    number = models.CharField(max_length=20, verbose_name='número', blank=True, null=True,
                              help_text="Caso não tenha, informar S/N.")
    complement = TextFieldWithInputText(blank=True, null=True, verbose_name='complemento')
    village = TextFieldWithInputText(blank=True, null=True, verbose_name='bairro')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='telefone',
                             validators=[phone_validator])

    user = models.OneToOneField(User, on_delete=models.PROTECT, blank=True, null=True, verbose_name='usuário',
                                related_name='person')
    avatar = models.ImageField(blank=True, null=True, verbose_name='foto')
    cpf = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='CPF',
                           validators=[cpf_validator])
    birth_date = models.DateField(blank=True, null=True,
                                  verbose_name='data nascimento')
    rg = TextFieldWithInputText(blank=True, null=True, verbose_name='rg')
    orgao_expedidor = TextFieldWithInputText(blank=True, null=True,
                                             verbose_name='orgão expedidor')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    synchronized = models.NullBooleanField(default=False)
    term_version = models.IntegerField(verbose_name='versão do termo de uso', blank=True, null=True)
    politics_version = models.IntegerField(verbose_name='versão da política de privacidade', blank=True, null=True)
    occupation = models.ForeignKey(Occupation, on_delete=models.SET_NULL, verbose_name='profissão', blank=True, null=True)

    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)
    has_user = models.BooleanField(verbose_name='vincular usuario?', default=False)

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
        rule.rule_4_desativa_usuario_ao_deletar_pessoa(self)
        super(Person, self).delete(*args, **kwargs)

    def clean(self):
        rule.rule_1_has_user_deve_ter_email(self)
        rule.rule_2_ja_existe_outro_usuario_com_mesmo_email(self)
        rule.rule_3_nao_remove_usuario_uma_vez_relacionado(self)

    def get_cpf_display(self):
        cpf = str(self.cpf)
        if not cpf:
            return ''
        return '{0}.{1}.{2}-{3}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:11])

    def get_birth_date_display(self):
        if not self.birth_date:
            return '--'
        return self.birth_date.strftime('%d/%m/%Y')
