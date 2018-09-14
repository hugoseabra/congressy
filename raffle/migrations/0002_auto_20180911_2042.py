# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-11 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='raffle',
            name='attended_only',
            field=models.BooleanField(default=True, help_text='Somente presentes (check-in) participarão do sorteio.', verbose_name='somente presentes'),
        ),
        migrations.AddField(
            model_name='raffle',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantos produtos serão sorteados?', verbose_name='Quantidade'),
        ),
    ]
