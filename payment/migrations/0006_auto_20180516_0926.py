# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-16 09:26
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_subscription', '0009_auto_20180329_1611'),
        ('payment', '0005_auto_20180427_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='credit_card_first_digits',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='credit_card_holder',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='credit_card_last_digits',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='installment_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True, verbose_name='valor da parcelas'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='installments',
            field=models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='parcelas'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='lot',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='gatheros_subscription.Lot'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='lot_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='manual',
            field=models.BooleanField(default=False, verbose_name='lançado manualmente'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='manual_author',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='author do pagamento manual'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='manual_payment_type',
            field=models.CharField(blank=True, choices=[('money', 'Dinheiro'), ('paycheck', 'Cheque'), ('debit_card', 'Cartão de Débito'), ('credit_card', 'Cartão de Crédito'), ('bank_deposit', 'Depósito'), ('bank_transfer', 'Transferência bancária'), ('waiting_payment', 'Aguardando pagamento')], max_length=30, null=True, verbose_name='tipo de recebimento manual'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date_created',
            field=models.DateTimeField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(blank=True, choices=[('boleto', 'Boleto'), ('credit_card', 'Cartão de credito'), ('manual', 'Manual')], max_length=30, null=True),
        ),
    ]
