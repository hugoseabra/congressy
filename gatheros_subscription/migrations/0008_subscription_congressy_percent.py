# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-18 18:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_subscription', '0007_auto_20180301_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='congressy_percent',
            field=models.CharField(choices=[('4.99', '4,99%'), ('6.00', '6%'), ('6.50', '6,5%'), ('7.00', '7%'), ('7.50', '7,5%'), ('8.00', '8%'), ('8.50', '8,5%'), ('9.00', '9%'), ('9.50', '9,5%'), ('10.00', '10%'), ('18.50', '18,5%'), ('25.0', '25,0%')], default='10.00', help_text='Valor percentual da congressy.', max_length=5, verbose_name='percentual congressy'),
        ),
    ]
