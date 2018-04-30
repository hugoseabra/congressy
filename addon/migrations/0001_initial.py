# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-30 16:43
from __future__ import unicode_literals

import base.models
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_subscription', '0011_auto_20180418_2232'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionalProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
            ],
            options={
                'verbose_name': 'tipo de opcional de produto',
                'ordering': ('name',),
                'verbose_name_plural': 'tipos de opcional de produto',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OptionalServiceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
            ],
            options={
                'verbose_name': 'tipo de opcional de serviço',
                'ordering': ('name',),
                'verbose_name_plural': 'tipos de opcional de serviço',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('date_end_sub', models.DateTimeField(help_text='Data e hora limite para se aceitar inscrições para este opcional.', verbose_name='Inscrição - data/hora limite')),
                ('published', models.BooleanField(default=True, verbose_name='publicado')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('created_by', models.CharField(max_length=255, verbose_name='criado por')),
                ('modified_by', models.CharField(max_length=255, verbose_name='modificado por')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=10, verbose_name='preço')),
                ('restrict_unique', models.BooleanField(default=False, help_text='Restringir como única dentro do intervalo de tempo.', verbose_name='restringir como único')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('quantity', models.PositiveIntegerField(blank=True, help_text='Limite máximo permitido.', null=True, verbose_name='quantidade')),
                ('release_days', models.PositiveIntegerField(blank=True, default=7, help_text='Número de dias em que serão liberadas as vagas de opcionais caso a inscrição esteja como pendente.', null=True, verbose_name='dias de liberação de opcionais')),
                ('lot_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_optionals', to='gatheros_subscription.LotCategory', verbose_name='categoria')),
                ('optional_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_type_optionals', to='addon.OptionalProductType', verbose_name='tipo')),
            ],
            options={
                'verbose_name': 'opcional de produto',
                'abstract': False,
                'ordering': ('name',),
                'verbose_name_plural': 'opcionais de produto',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('date_end_sub', models.DateTimeField(help_text='Data e hora limite para se aceitar inscrições para este opcional.', verbose_name='Inscrição - data/hora limite')),
                ('published', models.BooleanField(default=True, verbose_name='publicado')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('created_by', models.CharField(max_length=255, verbose_name='criado por')),
                ('modified_by', models.CharField(max_length=255, verbose_name='modificado por')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=10, verbose_name='preço')),
                ('restrict_unique', models.BooleanField(default=False, help_text='Restringir como única dentro do intervalo de tempo.', verbose_name='restringir como único')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('quantity', models.PositiveIntegerField(blank=True, help_text='Limite máximo permitido.', null=True, verbose_name='quantidade')),
                ('release_days', models.PositiveIntegerField(blank=True, default=7, help_text='Número de dias em que serão liberadas as vagas de opcionais caso a inscrição esteja como pendente.', null=True, verbose_name='dias de liberação de opcionais')),
                ('schedule_start', models.DateTimeField(help_text='Data e hora inicial da programação no dia do evento.', verbose_name='programação - data/hora inicial')),
                ('schedule_end', models.DateTimeField(help_text='Data e hora final da programação no dia do evento.', verbose_name='programação - data/hora final')),
                ('place', models.CharField(blank=True, max_length=255, null=True, verbose_name='local')),
                ('lot_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='service_optionals', to='gatheros_subscription.LotCategory', verbose_name='categoria')),
                ('optional_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='service_type_optionals', to='addon.OptionalServiceType', verbose_name='tipo')),
            ],
            options={
                'verbose_name': 'opcional de serviço',
                'abstract': False,
                'ordering': ('name',),
                'verbose_name_plural': 'opcionais de serviço',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data de criação')),
                ('optional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='addon.Product', verbose_name='opcional de produto')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptionproduct', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
            ],
            options={
                'verbose_name': 'inscrição de opcional de produto',
                'abstract': False,
                'ordering': ('subscription__event',),
                'verbose_name_plural': 'inscrições de opcional de produto',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data de criação')),
                ('optional', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='services', to='addon.Service', verbose_name='opcional de serviço')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptionservice', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
            ],
            options={
                'verbose_name': 'inscrição de opcional de serviço',
                'abstract': False,
                'ordering': ('subscription__event',),
                'verbose_name_plural': 'inscrições de opcional de serviço',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('limit', models.PositiveIntegerField(blank=True, help_text='Limitar número de inscrições de um mesmo participante em um mesmo tema.', null=True, verbose_name='limitar quantidade')),
            ],
            options={
                'verbose_name': 'tema',
                'ordering': ('name',),
                'verbose_name_plural': 'temas',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.AddField(
            model_name='service',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='services', to='addon.Theme', verbose_name='themas'),
        ),
    ]
