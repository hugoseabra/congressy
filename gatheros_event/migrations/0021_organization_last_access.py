# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-06 11:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0020_event_expected_subscriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='last_access',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
