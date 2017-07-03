from core.tests import GatherosTestCase
from gatheros_subscription.models import Field, Form


class FieldModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field'
    ]

    # noinspection PyMethodMayBeStatic
    def _get_form(self):
        return Form.objects.first()

    def _create_field(self, form=None, persist=False, **kwargs):
        if not form:
            form = self._get_form()

        data = {
            'form': form,
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'New one',
            'name': 'new field tests'
        }
        return self._create_model(
            model_class=Field,
            data=data,
            persist=persist,
            **kwargs
        )
