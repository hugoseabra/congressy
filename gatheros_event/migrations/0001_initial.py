# -*- coding: utf-8 -*-
# pylint: skip-file
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
import stdimage.models
import stdimage.validators
from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models

from core.model import validator
from gatheros_event.models.event import get_image_path
from gatheros_event.models.info import get_image_path as get_info_image_path


def load_initial_data(*_):
    print('\nLoading initial data:')
    call_command('loaddata', '001_segment', app_label='gatheros_event')
    call_command('loaddata', '002_subject', app_label='gatheros_event')
    call_command('loaddata', '003_occupation', app_label='gatheros_event')
    call_command('loaddata', '004_category', app_label='gatheros_event')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('kanu_locations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=255,
                    verbose_name='nome'
                )),
                ('active', models.BooleanField(
                    default=True,
                    verbose_name='ativo'
                )),
                ('description', models.TextField(
                    blank=True,
                    null=True,
                    verbose_name='descrição'
                )),
            ],
            options={
                'verbose_name': 'Categoria de Evento',
                'verbose_name_plural': 'Categorias de Evento',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=255,
                    verbose_name='nome'
                )),
                ('subscription_type', models.CharField(
                    choices=[
                        ('disabled', 'Desativadas'),
                        ('simple', 'Simples (gratuitas)'),
                        ('by_lots', 'Gerenciar por lotes')
                    ],
                    default='simple',
                    help_text='Como gostaria de gerenciar as inscrições de seu'
                              ' evento?',
                    max_length=15,
                    verbose_name='inscrições'
                )),
                ('subscription_offline', models.BooleanField(
                    default=False,
                    help_text='Ativar a sincronização para usar off-line no'
                              ' dia do evento.',
                    verbose_name='ativar inscrições off-line'
                )),
                ('date_start',
                 models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(verbose_name='data final')),
                ('banner_slide', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Banner de destaque (tamanho: 1140px x 500px)',
                    null=True,
                    upload_to=get_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(1140, 500),
                        stdimage.validators.MaxSizeValidator(2048, 898)
                    ],
                    verbose_name='banner destaque'
                )),
                ('banner_small', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Banner pequeno para apresentação geral'
                              ' (tamanho: 580px x 422px)',
                    null=True,
                    upload_to=get_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(580, 422),
                        stdimage.validators.MaxSizeValidator(1024, 745)
                    ],
                    verbose_name='banner pequeno'
                )),
                ('banner_top', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Banner para o topo do site do evento'
                              ' (tamanho: 1920px x 900px)',
                    null=True,
                    upload_to=get_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(1920, 900),
                        stdimage.validators.MaxSizeValidator(4096, 1920)
                    ],
                    verbose_name='banner topo do site'
                )),
                ('website', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('facebook', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('twitter', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('linkedin', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('skype', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('published', models.BooleanField(
                    default=False,
                    help_text='Eventos não publicados e com data futura serão'
                              ' considerados rascunhos.',
                    verbose_name='publicado'
                )),
                ('slug', models.SlugField(
                    editable=False,
                    max_length=128,
                    unique=True,
                    verbose_name='permalink'
                )),
            ],
            options={
                'verbose_name': 'evento',
                'verbose_name_plural': 'eventos',
                'ordering': ('name', 'pk', 'category__name'),
                'permissions': (
                    ('view_lots', 'Can view lots'),
                    ('add_lot', 'Can add lot'),
                ),
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('uuid', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                    unique=True
                )),
                ('created', models.DateTimeField(
                    verbose_name='criado em'
                )),
                ('expired', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='expira em'
                )),
                ('group', models.CharField(
                    choices=[
                        ('admin', 'Administrador'),
                        ('helper', 'Auxiliar')
                    ],
                    default='helper',
                    max_length=10,
                    verbose_name='grupo'
                )),
            ],
            options={
                'verbose_name': 'convite',
                'verbose_name_plural': 'convites',
                'ordering': ('created', 'author'),
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('group', models.CharField(
                    choices=[
                        ('admin', 'Administrador'),
                        ('helper', 'Auxiliar')
                    ],
                    max_length=20,
                    verbose_name='grupo'
                )),
                ('created', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='criado em'
                )),
                ('active', models.BooleanField(
                    default=True,
                    verbose_name='ativo'
                )),
            ],
            options={
                'verbose_name': 'membro',
                'verbose_name_plural': 'membros',
                'ordering': ['person', 'organization'],
            },
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=100, unique=True,
                    verbose_name='nome'
                )),
                ('active', models.BooleanField(
                    default=True,
                    verbose_name='ativo'
                )),
            ],
            options={
                'verbose_name': 'Profissão',
                'verbose_name_plural': 'Profissões',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=100,
                    verbose_name='nome'
                )),
                ('description', models.TextField(
                    blank=True,
                    null=True,
                    verbose_name='descrição (texto)'
                )),
                ('description_html', models.TextField(
                    blank=True,
                    null=True,
                    verbose_name='descrição (HTML)'
                )),
                ('avatar_width', models.PositiveIntegerField(
                    blank=True,
                    null=True
                )),
                ('avatar_height', models.PositiveIntegerField(
                    blank=True,
                    null=True
                )),
                ('avatar', models.ImageField(
                    blank=True,
                    height_field='avatar_height',
                    null=True,
                    upload_to='',
                    verbose_name='foto',
                    width_field='avatar_width'
                )),
                ('website', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('facebook', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('twitter', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('linkedin', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('skype', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('cash_provider', models.CharField(
                    blank=True,
                    max_length=10,
                    null=True,
                    verbose_name='provedor de recebimento'
                )),
                ('cash_data', models.CharField(
                    blank=True,
                    max_length=10,
                    null=True,
                    verbose_name='dados para recebimento'
                )),
                ('active', models.BooleanField(
                    default=True,
                    verbose_name='ativo'
                )),
                ('internal', models.BooleanField(
                    default=True,
                    verbose_name='interno'
                )),
                ('slug', models.SlugField(
                    max_length=128,
                    unique=True,
                    verbose_name='permalink',
                    help_text='Link que aparecerá para exibir as informações'
                              ' da organizações:'
                              ' https://gatheros.com/<permalink>'
                )),
            ],
            options={
                'verbose_name': 'organização',
                'verbose_name_plural': 'organizações',
                'ordering': ['name'],
                'permissions': (
                    ("can_invite", "Can invite members"),
                    ('can_view', 'Can view'),
                    ('can_add_event', 'Can add event'),
                    ("can_add_place", "Can add place related to organization"),
                ),
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('uuid', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                    unique=True
                )),
                ('name', models.CharField(
                    max_length=255,
                    verbose_name='nome'
                )),
                ('gender', models.CharField(
                    choices=[
                        ('M', 'Masculino'),
                        ('F', 'Feminino')
                    ],
                    max_length=1,
                    verbose_name='sexo'
                )),
                ('email', models.EmailField(
                    blank=True,
                    max_length=254,
                    null=True,
                    unique=True,
                    verbose_name='email'
                )),
                ('zip_code', models.CharField(
                    blank=True,
                    max_length=8,
                    null=True,
                    verbose_name='CEP'
                )),
                ('street', models.CharField(
                    max_length=255,
                    blank=True,
                    null=True,
                    verbose_name='endereço'
                )),
                ('number', models.CharField(
                    blank=True,
                    help_text='Caso não tenha, informar S/N.',
                    max_length=20,
                    null=True,
                    verbose_name='número'
                )),
                ('complement', models.CharField(
                    max_length=255,
                    blank=True,
                    null=True,
                    verbose_name='complemento'
                )),
                ('village', models.CharField(
                    max_length=255,
                    blank=True,
                    null=True,
                    verbose_name='bairro'
                )),
                ('phone', models.CharField(
                    blank=True,
                    max_length=12,
                    null=True,
                    validators=[validator.phone_validator],
                    verbose_name='telefone'
                )),
                ('avatar', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='',
                    verbose_name='foto'
                )),
                ('cpf', models.CharField(
                    blank=True,
                    max_length=11,
                    null=True,
                    unique=True,
                    validators=[validator.cpf_validator],
                    verbose_name='CPF')),
                ('birth_date', models.DateField(
                    blank=True,
                    null=True,
                    verbose_name='data nascimento'
                )),
                ('rg', models.CharField(
                    max_length=255,
                    blank=True,
                    null=True,
                    verbose_name='rg'
                )),
                ('orgao_expedidor', models.CharField(
                    max_length=255,
                    blank=True,
                    null=True,
                    verbose_name='orgão expedidor'
                )),
                ('created', models.DateTimeField(
                    auto_now_add=True,
                    null=True
                )),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('synchronized', models.NullBooleanField(default=False)),
                ('term_version', models.IntegerField(
                    blank=True, null=True,
                    verbose_name='versão do termo de uso'
                )),
                ('politics_version', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='versão da política de privacidade'
                )),
                ('pne', models.BooleanField(
                    default=False,
                    verbose_name='portador de necessidades especiais'
                )),
                ('website', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('facebook', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('twitter', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('linkedin', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('skype', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('city', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    to='kanu_locations.City',
                    verbose_name='cidade'
                )),
                ('occupation', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='gatheros_event.Occupation',
                    verbose_name='profissão'
                )),
                ('user', models.OneToOneField(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='person',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='usuário'
                )),
            ],
            options={
                'verbose_name': 'pessoa',
                'verbose_name_plural': 'pessoas',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=255,
                    verbose_name='nome'
                )),
                ('phone', models.CharField(
                    blank=True,
                    max_length=12,
                    null=True,
                    verbose_name='telefone'
                )),
                ('long', models.DecimalField(
                    blank=True,
                    decimal_places=3,
                    max_digits=8,
                    null=True
                )),
                ('lat', models.DecimalField(
                    blank=True,
                    decimal_places=3,
                    max_digits=8,
                    null=True
                )),
                ('zip_code', models.CharField(
                    blank=True,
                    max_length=8,
                    null=True,
                    verbose_name='CEP'
                )),
                ('street', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True,
                    verbose_name='logradouro (rua, avenida, etc.)'
                )),
                ('number', models.CharField(
                    blank=True,
                    help_text='Caso não tenha, informar S/N.',
                    max_length=20,
                    null=True,
                    verbose_name='número'
                )),
                ('complement', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True,
                    verbose_name='complemento'
                )),
                ('village', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True,
                    verbose_name='bairro'
                )),
                ('reference', models.CharField(
                    blank=True,
                    help_text='Alguma informação para ajudar a chegar ao'
                              ' local.',
                    max_length=255,
                    null=True,
                    verbose_name='referência'
                )),
                ('google_street_view_link', models.TextField(
                    blank=True,
                    help_text='Informações do Google StreetView para exibir'
                              ' imagens do local no site.',
                    null=True, verbose_name='Link do Google StreetView'
                )),
                ('city', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='kanu_locations.City',
                    verbose_name='cidade'
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='places',
                    to='gatheros_event.Organization',
                    verbose_name='organização'
                )),
            ],
            options={
                'verbose_name': 'local de Evento',
                'verbose_name_plural': 'locais de Evento',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=255,
                    verbose_name='nome'
                )),
                ('active', models.BooleanField(
                    default=True,
                    verbose_name='ativo'
                )),
                ('description', models.TextField(
                    blank=True,
                    null=True,
                    verbose_name='descrição'
                )),
            ],
            options={
                'verbose_name': 'Cadeia Produtiva',
                'verbose_name_plural': 'Cadeias Produtivas',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    max_length=255,
                    verbose_name='nome'
                )),
                ('active', models.BooleanField(
                    default=True,
                    verbose_name='ativo'
                )),
                ('description', models.TextField(
                    blank=True,
                    null=True,
                    verbose_name='descrição'
                )),
            ],
            options={
                'verbose_name': 'Assunto',
                'verbose_name_plural': 'Assuntos',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Info',
            fields=[
                ('description', models.TextField(
                    verbose_name='descrição (texto)'
                )),
                ('description_html', models.TextField(
                    verbose_name='descrição (HTML)'
                )),
                ('event', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    serialize=False,
                    to='gatheros_event.Event',
                    verbose_name='evento'
                )),
                ('config_type', models.CharField(
                    choices=[
                        ('text_only', 'Somente texto'),
                        ('image_main', 'Imagem única'
                                       ' (Largura 360px, Altura: livre)'),
                        ('4_images', '4 imagens pequenas'
                                     ' (Tamanho: 300px x 300px)'),
                        ('video', 'Vídeo (Youtube)')
                    ],
                    default='text_only',
                    max_length=15,
                    verbose_name='Exibição'
                )),
                ('image_main', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Imagem única da descrição do evento:'
                              ' 750px x 874px',
                    null=True,
                    upload_to=get_info_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(750, 874),
                        stdimage.validators.MaxSizeValidator(1400, 1400)
                    ],
                    verbose_name='imagem principal')
                 ),
                ('image1', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Tamanho: 350px x 350px',
                    null=True,
                    upload_to=get_info_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(350, 350),
                        stdimage.validators.MaxSizeValidator(1400, 1400)
                    ],
                    verbose_name='imagem pequena #1'
                )),
                ('image2', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Tamanho: 350px x 350px',
                    null=True,
                    upload_to=get_info_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(350, 350),
                        stdimage.validators.MaxSizeValidator(1400, 1400)
                    ],
                    verbose_name='imagem pequena #2'
                )),
                ('image3', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Tamanho: 350px x 350px',
                    null=True,
                    upload_to=get_info_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(350, 350),
                        stdimage.validators.MaxSizeValidator(1400, 1400)
                    ],
                    verbose_name='imagem pequena #3'
                )),
                ('image4', stdimage.models.StdImageField(
                    blank=True,
                    help_text='Tamanho: 350px x 350px',
                    null=True,
                    upload_to=get_info_image_path,
                    validators=[
                        stdimage.validators.MinSizeValidator(350, 350),
                        stdimage.validators.MaxSizeValidator(1400, 1400)
                    ],
                    verbose_name='imagem pequena #4'
                )),
                ('youtube_video_id', models.CharField(
                    blank=True,
                    help_text='Exemplo: '
                              'https://www.youtube.com/watch?v=id_do_video',
                    max_length=12,
                    null=True,
                    verbose_name='ID do Youtube'
                )),
            ],
            options={
                'verbose_name': 'Informação de Evento',
                'verbose_name_plural': 'Infomações de Eventos',
                'ordering': ['event'],
            },
        ),
        migrations.AddField(
            model_name='member',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='members',
                to='gatheros_event.Organization',
                verbose_name='organização'
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='person',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='members',
                to='gatheros_event.Person',
                verbose_name='pessoa'
            ),
        ),
        migrations.AddField(
            model_name='invitation',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='gatheros_event.Member',
                verbose_name='autor'
            ),
        ),
        migrations.AddField(
            model_name='invitation',
            name='to',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='invitations',
                to=settings.AUTH_USER_MODEL,
                verbose_name='convidado'
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='gatheros_event.Category',
                verbose_name='categoria'
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='events',
                to='gatheros_event.Organization',
                verbose_name='organização'
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.ForeignKey(
                blank=True,
                help_text='Deixar em branco se o evento é apenas on-line.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='gatheros_event.Place',
                verbose_name='local'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together=[('author', 'to')],
        ),
        migrations.RunPython(load_initial_data)
    ]
