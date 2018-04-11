# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-09 18:04
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_event', '0011_event_rsvp_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Associate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('email', models.EmailField(max_length=254, verbose_name='e-mail')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='associates', to='gatheros_event.Organization', verbose_name='organização')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Associados',
                'verbose_name': 'Associado',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
    ]
