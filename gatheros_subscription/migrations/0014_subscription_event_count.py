# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-17 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_subscription', '0013_subscription_test_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='event_count',
            field=models.IntegerField(blank=True, default=1, verbose_name='num. inscrição geral'),
        ),
    ]
