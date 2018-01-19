# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-17 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0002_auto_20180117_1658'),
        ('gatheros_subscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormConfig',
            fields=[
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='formconfig', serialize=False, to='gatheros_event.Event', verbose_name='evento')),
                ('email', models.BooleanField(default=False, verbose_name='e-mail obrigatório')),
                ('phone', models.BooleanField(default=False, verbose_name='celular obrigatório')),
                ('city', models.BooleanField(default=False, help_text='Caso você insirá o endereço, este campo será obrigatório por padrão.', verbose_name='cidade obrigatório')),
                ('cpf', models.CharField(choices=[('cpf-hide', 'Ocultar'), ('cpf-show', 'Mostrar'), ('cpf-required', 'Mostrar e Tornar obrigatório')], default='cpf-hide', help_text='Configuração do campo "CPF" no formulário.', max_length=25, verbose_name='CPF')),
                ('birth_date', models.CharField(choices=[('birth-date-hide', 'Ocultar'), ('birth-date-show', 'Mostrar'), ('birth-date-required', 'Mostrar e Tornar obrigatório')], default='birth-date-hide', help_text='Configuração do campo "Data de Nascimento" no formulário.', max_length=25, verbose_name='Data de Nascimento')),
                ('address', models.CharField(choices=[('address-hide', 'Ocultar'), ('address-show', 'Mostrar')], default='address-hide', help_text='Configuração do campo "Endereço" no formulário. Isto exigirá que alguns campos sejam obrigatórios.', max_length=25, verbose_name='Endereço')),
            ],
            options={
                'verbose_name_plural': 'Configurações de Formulário',
                'ordering': ['event'],
                'verbose_name': 'Configuração de formulário',
            },
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='answer',
            name='field',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='subscription',
        ),
        migrations.AlterUniqueTogether(
            name='defaultfieldoption',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='defaultfieldoption',
            name='field',
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='field',
            name='forms',
        ),
        migrations.RemoveField(
            model_name='field',
            name='organization',
        ),
        migrations.AlterUniqueTogether(
            name='fieldoption',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='fieldoption',
            name='field',
        ),
        migrations.RemoveField(
            model_name='form',
            name='event',
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.DeleteModel(
            name='DefaultField',
        ),
        migrations.DeleteModel(
            name='DefaultFieldOption',
        ),
        migrations.DeleteModel(
            name='Field',
        ),
        migrations.DeleteModel(
            name='FieldOption',
        ),
        migrations.DeleteModel(
            name='Form',
        ),
    ]
