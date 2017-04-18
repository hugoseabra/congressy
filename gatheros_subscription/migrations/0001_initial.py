# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-18 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_event', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True, verbose_name='valor')),
            ],
            options={
                'verbose_name_plural': 'respostas',
                'verbose_name': 'resposta',
                'ordering': ['field'],
            },
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('label', models.CharField(max_length=255, verbose_name='rótulo')),
                ('type', models.CharField(choices=[('input-text', 'INPUT-TEXT'), ('input-date', 'INPUT-DATE'), ('input-email', 'INPUT-EMAIL'), ('input-phone', 'INPUT-PHONE'), ('boolean', 'SIM/NÃO'), ('select', 'SELECT'), ('select-multiple', 'SELECT-MULTIPLE'), ('checkbox-group', 'CHECKBOX-GROUP'), ('radio-group', 'RADIO-GROUP')], default='input-text', max_length=20, verbose_name='tipo')),
                ('order', models.PositiveIntegerField(blank=True, null=True, verbose_name='ordem')),
                ('form_default_field', models.BooleanField(default=False, verbose_name='campo fixo')),
                ('required', models.BooleanField(default=False, verbose_name='obrigatório')),
                ('instruction', models.TextField(blank=True, null=True, verbose_name='instrução')),
                ('placeholder', models.CharField(blank=True, max_length=100, null=True, verbose_name='placeholder')),
                ('default_value', models.TextField(blank=True, null=True, verbose_name='valor padrão')),
            ],
            options={
                'verbose_name_plural': 'Campos de Formulário',
                'ordering': ['form__id', 'order', 'name'],
                'verbose_name': 'Campo de Formulário',
            },
        ),
        migrations.CreateModel(
            name='FieldOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='rótulo')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='valor')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='gatheros_subscription.Field', verbose_name='campo')),
            ],
            options={
                'verbose_name_plural': 'Opções de Campo',
                'ordering': ['field__form__id', 'field__id', 'name'],
                'verbose_name': 'Opção de Campo',
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='form', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name_plural': 'formulários de eventos',
                'ordering': ['event'],
                'verbose_name': 'formulário de evento',
            },
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(blank=True, null=True, verbose_name='data final')),
                ('limit', models.PositiveIntegerField(blank=True, null=True, verbose_name='limite')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='preco')),
                ('tax', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='taxa')),
                ('discount_type', models.CharField(blank=True, choices=[('percent', '%'), ('money', 'R$')], default='percent', max_length=15, null=True, verbose_name='tipo de desconto')),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='desconto')),
                ('promo_code', models.CharField(blank=True, max_length=15, null=True, verbose_name='código promocional')),
                ('transfer_tax', models.BooleanField(default=False, verbose_name='trasferir taxa para participante')),
                ('private', models.BooleanField(default=False, verbose_name='privado')),
                ('internal', models.BooleanField(default=True, verbose_name='gerado internamente')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lots', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name_plural': 'lotes',
                'ordering': ['pk', 'name', 'event'],
                'verbose_name': 'lote',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('origin', models.CharField(choices=[('web', 'WEB'), ('offline', 'Sincronização Off-line')], default='web', max_length=15, verbose_name='origem')),
                ('created_by', models.PositiveIntegerField(verbose_name='criado por')),
                ('attended', models.BooleanField(default=False, verbose_name='compareceu')),
                ('code', models.CharField(blank=True, max_length=15, verbose_name='código')),
                ('count', models.IntegerField(blank=True, default=None, verbose_name='num. inscrição')),
                ('attended_on', models.DateTimeField(blank=True, null=True, verbose_name='confirmado em')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('modified', models.DateTimeField(auto_now_add=True, verbose_name='modificado em')),
                ('synchronized', models.BooleanField(default=False)),
                ('event', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='gatheros_event.Event', verbose_name='evento')),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='gatheros_subscription.Lot', verbose_name='lote')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='gatheros_event.Person', verbose_name='pessoa')),
            ],
            options={
                'verbose_name_plural': 'Inscrições',
                'verbose_name': 'Inscrição',
                'ordering': ['person', 'event'],
            },
        ),
        migrations.AddField(
            model_name='field',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='gatheros_subscription.Form', verbose_name='formulário'),
        ),
        migrations.AddField(
            model_name='answer',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='gatheros_subscription.Field', verbose_name='campo'),
        ),
        migrations.AddField(
            model_name='answer',
            name='subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='gatheros_subscription.Subscription', verbose_name='inscrição'),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('event', 'code'), ('person', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('subscription', 'field')]),
        ),
    ]
