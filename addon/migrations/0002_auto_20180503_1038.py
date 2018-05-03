# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-03 10:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionproduct',
            name='optional_liquid_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionproduct',
            name='optional_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionservice',
            name='optional_liquid_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionservice',
            name='optional_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
    ]
