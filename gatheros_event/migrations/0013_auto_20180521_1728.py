# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-21 17:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0012_auto_20180521_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_scientific',
            field=models.BooleanField(default=False, verbose_name='evento científico'),
        ),
        migrations.AddField(
            model_name='info',
            name='editorial_body',
            field=models.TextField(blank=True, null=True, verbose_name='corpo editorial de evento cientifico'),
        ),
        migrations.AddField(
            model_name='info',
            name='scientific_rules',
            field=models.TextField(blank=True, null=True, verbose_name='normas de evento cientifico'),
        ),
    ]
