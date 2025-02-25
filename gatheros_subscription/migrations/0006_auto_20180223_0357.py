# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-23 03:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gatheros_subscription', '0005_auto_20180220_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='status',
            field=models.CharField(
                choices=[
                    ('confirmed', 'Confirmado'),
                    ('canceled', 'Cancelado'),
                    ('awaiting', 'Pendente')
                ],
                default='awaiting',
                max_length=15,
                verbose_name='status'
            ),
        ),
        migrations.AlterField(
            model_name='lot',
            name='transfer_tax',
            field=models.BooleanField(
                default=False,
                help_text='Repasse a taxa para o participante e receba o valor'
                          ' integral do ingresso.',
                verbose_name='repassar taxa'),
        ),
    ]
