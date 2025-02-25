# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-24 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_subscription', '0015_auto_20180912_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='attended',
            field=models.BooleanField(default=False, verbose_name='compareceu'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='attended_on',
            field=models.DateTimeField(blank=True, null=True, verbose_name='confirmado em'),
        ),
    ]
