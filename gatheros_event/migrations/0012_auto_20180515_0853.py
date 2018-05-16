# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-15 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0011_auto_20180427_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='congressy_percent',
            field=models.CharField(choices=[('4.99', '4,99%'), ('7.00', '7%'), ('10.00', '10%'), ('8.50', '8,5%')], default='10.00', help_text='Valor percentual da congressy caso o evento seja pago.', max_length=5, verbose_name='percentual congressy'),
        ),
    ]
