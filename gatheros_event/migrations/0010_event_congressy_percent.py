# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-18 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0009_auto_20180314_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='congressy_percent',
            field=models.CharField(choices=[(8.5, '8,5%'), (10.0, '10%')], default=10.0, help_text='Valor percentual da congressy caso o evento seja pago.', max_length=15, verbose_name='percentual congressy'),
        ),
    ]
