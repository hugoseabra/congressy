# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-07 14:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_bankaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='boleto_expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='vencimento do boleto'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='boleto_url',
            field=models.TextField(blank=True, null=True, verbose_name='URL do boleto'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='liquid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True, verbose_name='valor líquido do organizador'),
        ),
    ]
