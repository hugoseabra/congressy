# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-24 22:51
from __future__ import unicode_literals

import uuid

from django.core.management import call_command
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import gatheros_event.models.event
import gatheros_event.models.person
from gatheros_event.lib import validators


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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', gatheros_event.models.event.TextFieldWithInputText(verbose_name='nome')),
                ('subscription_type', models.CharField(choices=[('disabled', 'Desativado'), ('simple', 'Simples'), ('by_lots', 'Por lotes')], default='simple', max_length=15, verbose_name='inscrições')),
                ('subscription_online', models.BooleanField(default=True, verbose_name='ativar inscrições on-line')),
                ('subscription_offline', models.BooleanField(default=False, help_text='Ativa a sincronização para secretaria', verbose_name='ativar inscrições off-line')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(verbose_name='data final')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('website', models.CharField(blank=True, max_length=255, null=True)),
                ('facebook', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter', models.CharField(blank=True, max_length=255, null=True)),
                ('linkedin', models.CharField(blank=True, max_length=255, null=True)),
                ('skype', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'evento',
                'verbose_name_plural': 'eventos',
                'ordering': ('name', 'pk', 'category__name'),
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(verbose_name='criado em')),
                ('expired', models.DateTimeField(blank=True, null=True, verbose_name='expira em')),
                ('type', models.CharField(choices=[('helper', 'Auxiliar'), ('admin', 'Administrador')], default='helper', max_length=10, verbose_name='tipo')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(choices=[('admin', 'Administrador'), ('helper', 'Auxiliar')], max_length=20, verbose_name='grupo')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('created_by', models.PositiveIntegerField(verbose_name='criado por')),
                ('invited_on', models.DateTimeField(auto_now_add=True, verbose_name='convidado em')),
                ('invitation_accepted', models.BooleanField(default=False, verbose_name='convite aceito')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nome')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='nome')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('avatar_width', models.PositiveIntegerField(blank=True, null=True)),
                ('avatar_height', models.PositiveIntegerField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, height_field='avatar_height', null=True, upload_to='', verbose_name='foto', width_field='avatar_width')),
                ('website', models.CharField(blank=True, max_length=255, null=True)),
                ('facebook', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter', models.CharField(blank=True, max_length=255, null=True)),
                ('linkedin', models.CharField(blank=True, max_length=255, null=True)),
                ('skype', models.CharField(blank=True, max_length=255, null=True)),
                ('cash_provider', models.CharField(blank=True, max_length=10, null=True, verbose_name='provedor de recebimento')),
                ('cash_data', models.CharField(blank=True, max_length=10, null=True, verbose_name='dados para recebimento')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('internal', models.BooleanField(default=True, verbose_name='gerado internamente')),
            ],
            options={
                'verbose_name': 'organização',
                'verbose_name_plural': 'organizações',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', gatheros_event.models.person.TextFieldWithInputText(verbose_name='nome')),
                ('genre', models.CharField(choices=[('M', 'Masculino'), ('F', 'Feminino')], max_length=1, verbose_name='sexo')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='email')),
                ('zip_code', models.CharField(blank=True, max_length=8, null=True, verbose_name='CEP')),
                ('street', gatheros_event.models.person.TextFieldWithInputText(blank=True, null=True, verbose_name='endereço')),
                ('complement', gatheros_event.models.person.TextFieldWithInputText(blank=True, null=True, verbose_name='complemento')),
                ('village', gatheros_event.models.person.TextFieldWithInputText(blank=True, null=True, verbose_name='bairro')),
                ('phone', models.TextField(blank=True, null=True, validators=[validators.phone_validator], verbose_name='telefone')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='', verbose_name='foto')),
                ('cpf', models.CharField(blank=True, max_length=11, null=True, unique=True, validators=[validators.cpf_validator], verbose_name='CPF')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='data nascimento')),
                ('rg', gatheros_event.models.person.TextFieldWithInputText(blank=True, null=True, verbose_name='rg')),
                ('orgao_expedidor', gatheros_event.models.person.TextFieldWithInputText(blank=True, null=True, verbose_name='orgão expedidor')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('synchronized', models.NullBooleanField(default=False)),
                ('term_version', models.IntegerField(blank=True, null=True, verbose_name='versão do termo de uso')),
                ('politics_version', models.IntegerField(blank=True, null=True, verbose_name='versão da política de privacidade')),
                ('website', models.CharField(blank=True, max_length=255, null=True)),
                ('facebook', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter', models.CharField(blank=True, max_length=255, null=True)),
                ('linkedin', models.CharField(blank=True, max_length=255, null=True)),
                ('skype', models.CharField(blank=True, max_length=255, null=True)),
                ('has_user', models.BooleanField(default=False, verbose_name='vincular usuario?')),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kanu_locations.City', verbose_name='cidade')),
                ('occupation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gatheros_event.Occupation', verbose_name='profissão')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='person', to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('phone', models.CharField(blank=True, max_length=9, null=True, verbose_name='telefone')),
                ('long', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('lat', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=8, null=True, verbose_name='CEP')),
                ('street', models.CharField(blank=True, max_length=255, null=True, verbose_name='logradouro (rua, avenida, etc.)')),
                ('complement', models.CharField(blank=True, max_length=255, null=True, verbose_name='complemento')),
                ('village', models.CharField(blank=True, max_length=255, null=True, verbose_name='bairro')),
                ('reference', models.CharField(blank=True, max_length=255, null=True, verbose_name='referência')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kanu_locations.City', verbose_name='cidade')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='gatheros_event.Organization', verbose_name='organização')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
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
                ('text', models.TextField(verbose_name='texto')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='gatheros_event.Event', verbose_name='evento')),
                ('image1', models.ImageField(blank=True, null=True, upload_to='', verbose_name='imagem 1')),
                ('image2', models.ImageField(blank=True, null=True, upload_to='', verbose_name='imagem 2')),
                ('image3', models.ImageField(blank=True, null=True, upload_to='', verbose_name='imagem 3')),
                ('image4', models.ImageField(blank=True, null=True, upload_to='', verbose_name='imagem 4')),
                ('video', models.FileField(blank=True, null=True, upload_to='', verbose_name='vídeo')),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='gatheros_event.Organization', verbose_name='organização'),
        ),
        migrations.AddField(
            model_name='member',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='gatheros_event.Person', verbose_name='pessoa'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gatheros_event.Member', verbose_name='autor'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to=settings.AUTH_USER_MODEL, verbose_name='convidado'),
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gatheros_event.Category', verbose_name='categoria'),
        ),
        migrations.AddField(
            model_name='event',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gatheros_event.Organization', verbose_name='organização'),
        ),
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gatheros_event.Place', verbose_name='local'),
        ),
        migrations.RunPython(load_initial_data)
    ]
