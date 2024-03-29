# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-24 01:46
from __future__ import unicode_literals

import base.models
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_auto_20190521_1816'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payable',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('pagarme_id', models.CharField(editable=False, max_length=28, verbose_name='ID de recebível (pagar.me)')),
                ('status', models.CharField(blank=True, choices=[('waiting_funds', 'Aguardando saldo'), ('prepaid', 'Em processo de pagamento'), ('paid', 'Pago (disponível)'), ('suspended', 'Suspenso')], default='waiting_funds', max_length=15, verbose_name='status')),
                ('type', models.CharField(choices=[('credit', 'Crédito'), ('refund', 'Estono'), ('chargeback', 'Chargeback'), ('chargeback_refund', 'Estono de chargeback'), ('block', 'Bloqueado'), ('unblock', 'Desbloqueado')], max_length=15, verbose_name='tipo')),
                ('installment', models.PositiveIntegerField(editable=False, verbose_name='parcela')),
                ('amount', models.DecimalField(decimal_places=10, default=Decimal('0'), max_digits=25, verbose_name='montante')),
                ('fee', models.DecimalField(decimal_places=10, default=Decimal('0'), max_digits=25, null=True, verbose_name='custo de transação')),
                ('antecipation_fee', models.DecimalField(decimal_places=10, default=Decimal('0'), max_digits=25, null=True, verbose_name='custo de antecipação')),
                ('recipient_id', models.CharField(editable=False, max_length=28, verbose_name='ID recebedor (pagar.me)')),
                ('created', models.DateTimeField(editable=False, verbose_name='criado em')),
                ('payment_date', models.DateTimeField(null=True, verbose_name='pago em')),
                ('modified', models.DateTimeField(null=True, verbose_name='modificado em')),
                ('next_check', models.DateTimeField(null=True, verbose_name='próxima verificação em')),
            ],
            options={
                'verbose_name': 'Item pagável',
                'verbose_name_plural': 'Itens pagáveis',
            },
            bases=(models.Model, base.models.EntityMixin),
        ),
        migrations.CreateModel(
            name='SplitRule',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('pagarme_id', models.CharField(editable=False, max_length=28, verbose_name='ID de regra (pagar.me)')),
                ('is_congressy', models.BooleanField(verbose_name='se congressy')),
                ('charge_processing_fee', models.BooleanField(default=False, verbose_name='responsável pelas taxas')),
                ('amount', models.DecimalField(decimal_places=10, default=Decimal('0'), max_digits=25, verbose_name='montante')),
                ('recipient_id', models.CharField(editable=False, max_length=28, verbose_name='ID recebedor (pagar.me)')),
                ('created', models.DateTimeField(editable=False, verbose_name='criado em')),
            ],
            options={
                'verbose_name': 'Regra de Rateamento',
                'verbose_name_plural': 'Regras de rateamento',
            },
            bases=(models.Model, base.models.EntityMixin),
        ),
        migrations.AddField(
            model_name='transaction',
            name='pagarme_id',
            field=models.PositiveIntegerField(editable=False, null=True, verbose_name='ID da transação (pagar.me)'),
        ),
        migrations.AddField(
            model_name='splitrule',
            name='transaction',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='split_rules', to='payment.Transaction', verbose_name='transação'),
        ),
        migrations.AddField(
            model_name='payable',
            name='split_rule',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payables', to='payment.SplitRule', verbose_name='regra de rateamento'),
        ),
    ]
