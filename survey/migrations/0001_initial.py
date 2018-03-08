# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-08 11:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nome da opção', max_length=255, verbose_name='nome')),
                ('value', models.CharField(help_text='Valor da opção', max_length=255, verbose_name='valor')),
            ],
            options={
                'verbose_name': 'Opção de uma pergunta',
                'verbose_name_plural': 'Opções de uma pergunta',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Título da pergunta', max_length=255, verbose_name='titulo')),
                ('is_required', models.BooleanField(default=False, help_text='Obrigatoriedade da pergunta', verbose_name='obrigatoriedade')),
                ('is_complex', models.BooleanField(default=False, help_text='Pergunta possui opções.', verbose_name='pergunta com opções')),
            ],
            options={
                'verbose_name': 'Pergunta de Questionario',
                'verbose_name_plural': 'Perguntas de Questionario',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nome do questionario', max_length=255, verbose_name='nome')),
            ],
            options={
                'verbose_name': 'questionario',
                'verbose_name_plural': 'questionarios',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey', verbose_name='questionario'),
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Question', verbose_name='pergunta'),
        ),
    ]
