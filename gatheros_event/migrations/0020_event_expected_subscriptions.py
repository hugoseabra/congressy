# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-27 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0019_auto_20180622_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='expected_subscriptions',
            field=models.PositiveIntegerField(blank=True, help_text='Quantas pessoas você espera no seu evento ?', null=True, verbose_name='Número esperado de participantes'),
        ),
    ]
