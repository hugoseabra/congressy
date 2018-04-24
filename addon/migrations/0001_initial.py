# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-23 19:42
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_subscription', '0011_auto_20180418_2232'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionalProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(verbose_name='data final')),
                ('description', models.TextField(verbose_name='descrição')),
                ('quantity', models.PositiveIntegerField(blank=True, null=True, verbose_name='quantidade')),
                ('published', models.BooleanField(default=True, verbose_name='publicado')),
                ('has_cost', models.BooleanField(default=False, verbose_name='possui custo')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='modificado')),
                ('created_by', models.CharField(editable=False, max_length=255, null=True, verbose_name='criado por')),
                ('modified_by', models.CharField(blank=True, max_length=255, null=True, verbose_name='modificado por')),
                ('lot_categories', models.ManyToManyField(related_name='optionalproduct_optionals', to='gatheros_subscription.LotCategory', verbose_name='categorias')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OptionalService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(verbose_name='data final')),
                ('description', models.TextField(verbose_name='descrição')),
                ('quantity', models.PositiveIntegerField(blank=True, null=True, verbose_name='quantidade')),
                ('published', models.BooleanField(default=True, verbose_name='publicado')),
                ('has_cost', models.BooleanField(default=False, verbose_name='possui custo')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='modificado')),
                ('created_by', models.CharField(editable=False, max_length=255, null=True, verbose_name='criado por')),
                ('modified_by', models.CharField(blank=True, max_length=255, null=True, verbose_name='modificado por')),
                ('place', models.CharField(blank=True, max_length=255, null=True, verbose_name='local')),
                ('session_restriction', models.NullBooleanField(default=False, help_text='Participante poderá participar de apenas um sessão por vez.', verbose_name='restringir por sessão')),
                ('theme_limit', models.PositiveIntegerField(blank=True, help_text='Participante poderá adquirir opcionais dentro de um limite por tema.', null=True, verbose_name='limitar por tema')),
                ('lot_categories', models.ManyToManyField(related_name='optionalservice_optionals', to='gatheros_subscription.LotCategory', verbose_name='categorias')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OptionalType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
            ],
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(verbose_name='data final')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço')),
                ('lot_category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='productprice_prices', to='gatheros_subscription.LotCategory')),
                ('optional_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='addon.OptionalProduct')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ServicePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(verbose_name='data final')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço')),
                ('lot_category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='serviceprice_prices', to='gatheros_subscription.LotCategory')),
                ('optional_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='addon.OptionalService')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionOptionalProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data de criação')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço')),
                ('count', models.PositiveIntegerField(blank=True, default=0, verbose_name='quantidade até agora')),
                ('total_allowed', models.PositiveIntegerField(verbose_name='total permitido')),
                ('optional_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='addon.OptionalProduct', verbose_name='opcional de produto')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptionoptionalproduct_optionals', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionOptionalService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data de criação')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço')),
                ('count', models.PositiveIntegerField(blank=True, default=0, verbose_name='quantidade até agora')),
                ('total_allowed', models.PositiveIntegerField(verbose_name='total permitido')),
                ('optional_service', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='services', to='addon.OptionalService', verbose_name='opcional de serviço')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptionoptionalservice_optionals', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
            ],
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.AddField(
            model_name='optionalservice',
            name='optional_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='optionalservice_optionals', to='addon.OptionalType', verbose_name='tipo'),
        ),
        migrations.AddField(
            model_name='optionalservice',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='services', to='addon.Theme', verbose_name='themas'),
        ),
        migrations.AddField(
            model_name='optionalproduct',
            name='optional_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='optionalproduct_optionals', to='addon.OptionalType', verbose_name='tipo'),
        ),
    ]
