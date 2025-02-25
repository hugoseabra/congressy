# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-04-10 16:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_event', '0036_featuremanagement_videos'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoConfig',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('token', models.CharField(max_length=64, verbose_name='token')),
                ('project_pk', models.UUIDField(verbose_name='project pk')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='video_config', to='gatheros_event.Event', verbose_name='event')),
            ],
            options={
                'verbose_name_plural': 'Configurações de vídeo',
                'verbose_name': 'Configuração de vídeo',
            },
        ),
    ]
