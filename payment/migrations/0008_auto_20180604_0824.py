# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-04 08:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='liquid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
    ]
