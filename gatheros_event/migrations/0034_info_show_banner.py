# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-23 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0033_auto_20191220_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='show_banner',
            field=models.BooleanField(default=True, verbose_name='Mostrar banner no hotsite'),
        ),
    ]
