from django.test import TestCase

from gatheros_subscription.models import Field, Form


class FieldModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '001_form',
        '002_field'
    ]

    def test_new_field_always_last_one(self):
        form = Form.objects.first()
        last_order = form.fields.order_by('-order').first().order

        field = Field.objects.create(
            form=form,
            name='new field tests',
            label='New one',
            type=Field.FIELD_INPUT_TEXT,
        )

        self.assertEqual(field.order, last_order + 1)
