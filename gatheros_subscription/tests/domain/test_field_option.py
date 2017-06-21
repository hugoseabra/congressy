from core.tests import GatherosTestCase
from gatheros_subscription.models import Field, FieldOption
from gatheros_subscription.models.rules import field_option as rule


class TestModelFieldOption(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '004_category',
        '007_organization',
        '009_place',
        '010_event',
        '002_form',
        '003_field',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_field(self):
        field = Field.objects.last()
        # Forcing to test
        field.type = Field.FIELD_SELECT
        field.with_options = True
        field.save()
        return field

    def _create_field_option(self, field=None, **kwargs):
        if not field:
            field = self._get_field()
        data = {
            'field': field,
            'name': 'Field test',
            'value': 'Field test'
        }
        return self._create_model(model_class=FieldOption, data=data, **kwargs)

    def test_rule_1_somente_campos_com_opcoes(self):
        rule_callback = rule.rule_1_somente_campos_com_opcoes

        field_option = self._create_field_option()
        field_option.field.field_type = Field.FIELD_INPUT_TEXT
        field_option.field.save()

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[field_option],
            field='field'
        )

        """ MODEL """
        self._trigger_validation_error(
            callback=field_option.save,
            field='field'
        )

        """ FUNCIONANDO """
        field_option.field.field_type = Field.FIELD_RADIO_GROUP
        field_option.field.save()
        field_option.save()
