# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-18 17:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addon', '0005_auto_20190313_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriptionproduct',
            name='optional_liquid_price',
        ),
        migrations.RemoveField(
            model_name='subscriptionproduct',
            name='optional_price',
        ),
        migrations.RemoveField(
            model_name='subscriptionservice',
            name='optional_liquid_price',
        ),
        migrations.RemoveField(
            model_name='subscriptionservice',
            name='optional_price',
        ),
    ]