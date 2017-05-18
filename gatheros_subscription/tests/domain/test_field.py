from core.tests import GatherosTestCase
from gatheros_subscription.models import Field, Form


class FieldModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '002_form',
        '003_field'
    ]

    # noinspection PyMethodMayBeStatic
    def _get_form(self):
        return Form.objects.first()

    def _create_field(self, form=None, persist=False, **kwargs):
        if not form:
            form = self._get_form()

        data = {
            'form': form,
            'type': Field.FIELD_INPUT_TEXT,
            'label': 'New one',
            'name': 'new field tests'
        }
        return self._create_model(
            model_class=Field,
            data=data,
            persist=persist,
            **kwargs
        )

    def test_new_field_always_last_one(self):
        form = Form.objects.first()
        last_order = form.fields.order_by('-order').first().order

        field = self._create_field(form=form, persist=True)

        self.assertEqual(field.order, last_order + 1)
