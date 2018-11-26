# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-26 00:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_transaction_installment_part'),
        ('installment', '0002_auto_20181123_1505'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='part',
            options={'ordering': ['expiration_date'], 'verbose_name': 'Parcela de Contrato', 'verbose_name_plural': 'Parcelas de Contrato'},
        ),
        migrations.AddField(
            model_name='part',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='part_transaction', to='payment.Transaction', verbose_name='transação da parcela'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.CharField(blank=True, choices=[('open', 'aberto'), ('cancelled', 'cancelado'), ('fully_paid', 'quitado')], default='open', max_length=20, verbose_name='status'),
        ),
    ]
