# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-01 13:32
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.db.models.deletion
import gatheros_event.models.mixins.gatheros_model_mixin
import sync.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_event', '0030_auto_20190617_1909'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('key', models.CharField(editable=False, help_text='Chave de sincronização que libera a capacidade do cliente de sincronizar dados na plataforma.', max_length=40, verbose_name='chave')),
                ('active', models.BooleanField(default=False, verbose_name='ativo')),
                ('last_sync', models.DateTimeField(auto_now_add=True, verbose_name='última sincronização')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modificado em')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sync_clients', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name_plural': 'clientes de sincronização',
                'verbose_name': 'cliente de sincronização',
            },
            bases=(gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin, base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SyncQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modificado em')),
                ('file_path', models.FileField(help_text='Caminho do arquivo JSON a ser processado na sincronização', upload_to=sync.models.get_file_path, validators=[sync.models.validate_json_only_file], verbose_name='arquivo de sincronização')),
                ('status', models.CharField(choices=[('not_started', 'Não iniciado'), ('running', 'Em andamento'), ('processed', 'Processado'), ('processed', 'Cancelado'), ('invalid', 'Inválido')], default='not_started', max_length=12, null=True, verbose_name='Status')),
                ('error_message', models.TextField(blank=True, editable=False, null=True, verbose_name='Mensagens de erro')),
                ('warning_message', models.TextField(blank=True, editable=False, null=True, verbose_name='Mensagens de alerta')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='queues', to='sync.SyncClient', verbose_name='cliente de sincronização')),
            ],
            options={
                'verbose_name_plural': 'filas de sincronização',
                'verbose_name': 'fila de sincronização',
            },
            bases=(gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin, base.models.EntityMixin, models.Model),
        ),
    ]