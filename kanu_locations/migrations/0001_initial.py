# -*- coding: utf-8 -*-
import sys

from django.db import migrations, models
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    if 'test' in sys.argv:
        call_command("loaddata", "kanu_locations_city_test")
        return True

    call_command("loaddata", "kanu_locations_city")


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('name_ascii', models.CharField(max_length=255)),
                ('uf', models.CharField(max_length=2)),
            ],
            options={
                'ordering': ['name_ascii'],
            },
        ),
        migrations.RunPython(load_fixture)
    ]
