# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-09 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0004_auto_20180202_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='function',
            field=models.CharField(blank=True, help_text='Cargo ou função que exerce profissialmente.', max_length=255, null=True, verbose_name='Cargo/Função'),
        ),
        migrations.AddField(
            model_name='person',
            name='institution',
            field=models.CharField(blank=True, help_text='Empresa, Igreja, Fundação, etc.', max_length=255, null=True, verbose_name='Empresa/Instituição'),
        ),
    ]