# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-23 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_subscription', '0002_auto_20180119_0223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lot',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='valor'),
        ),
        migrations.AlterField(
            model_name='lot',
            name='transfer_tax',
            field=models.BooleanField(default=False, help_text='Repasse a taxa para o participante e receba o valor integral do ingresso.', verbose_name='trasferir taxa para participante'),
        ),
    ]
