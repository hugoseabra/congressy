# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-11 16:42
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
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('value', models.CharField(max_length=255, verbose_name='valor')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('intro', models.BooleanField(default=False)),
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
                ('type', models.CharField(max_length=50, verbose_name='tipo')),
                ('label', models.CharField(max_length=255, verbose_name='rotulo')),
                ('name', models.CharField(max_length=255, verbose_name='titulo')),
                ('required', models.BooleanField(default=False, verbose_name='obrigatoriedade')),
                ('help_text', models.CharField(max_length=255, verbose_name='texto de ajuda')),
                ('has_options', models.BooleanField(default=False, verbose_name='pergunta com opções')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
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
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
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
