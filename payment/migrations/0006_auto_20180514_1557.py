# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-14 15:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20180427_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='manual',
            field=models.BooleanField(default=False, verbose_name='lançado manualmente'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='manual_payment_type',
            field=models.CharField(blank=True, choices=[('money', 'Dinheiro'), ('paycheck', 'Chegue'), ('debit_card', 'Cartão de Débito'), ('credit_card', 'Cartão de Crédito')], max_length=30, null=True, verbose_name='tipo de recebimento manual'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='manual_registered_by',
            field=models.CharField(blank=True, editable=False, max_length=120, null=True, verbose_name='registrado por'),
        ),
    ]
