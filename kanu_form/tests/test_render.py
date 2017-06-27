from django.test import TestCase

from kanu_form.field_manager import FieldManager
from kanu_form.fields.field import Field
from kanu_form.forms import KanuForm


class FormRenderTest(TestCase):
    def test_render_input_text(self):

        manager = FieldManager()
        manager.create(
            name='name',
            field_type=Field.FIELD_INPUT_TEXT,
            label='nome',
            required=True,
            max_length=10
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="text"',
            'required',
            'maxlength="10"',
            'id="id_name"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_number(self):
        manager = FieldManager()
        manager.create(
            name='name',
            field_type=Field.FIELD_INPUT_NUMBER,
            label='nome',
            required=True,
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="number"',
            'required',
            'id="id_name"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_date(self):

        manager = FieldManager()
        manager.create(
            name='some_date',
            field_type=Field.FIELD_INPUT_DATE,
            label='date',
            required=True
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="date"',
            'required',
            'id="id_some_date"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_datetime(self):
        manager = FieldManager()
        manager.create(
            name='some_datetime',
            field_type=Field.FIELD_INPUT_DATETIME,
            label='datetime',
            required=True
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="datetime-local"',
            'required',
            'id="id_some_datetime"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_email(self):

        manager = FieldManager()
        manager.create(
            name='some_email',
            field_type=Field.FIELD_INPUT_EMAIL,
            label='e-mail',
            required=True
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="email"',
            'required',
            'id="id_some_email"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_tel(self):

        manager = FieldManager()
        manager.create(
            name='some_tel',
            field_type=Field.FIELD_INPUT_PHONE,
            label='celular',
            required=True
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="tel"',
            'required',
            'maxlength="18"',
            'id="id_some_tel"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_textarea(self):
        manager = FieldManager()
        manager.create(
            name='textarea_example',
            field_type=Field.FIELD_TEXTAREA,
            label='my textarea',
            required=True
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'textarea',
            'required',
            'rows="10"',
            'cols="40"',
            'id="id_textarea_example"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_boolean(self):
        manager = FieldManager()
        manager.create(
            name='boolean-field',
            field_type=Field.FIELD_BOOLEAN,
            label='my boolean field',
            required=True
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'input',
            'type="checkbox"',
            'id="id_boolean-field"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_select(self):
        manager = FieldManager()

        options = [
            ('option 1', 'Option 1'),
            ('option 2', 'Option 2'),
            ('option 3', 'Option 3'),
        ]

        manager.create(
            name='select-field',
            field_type=Field.FIELD_SELECT,
            label='my select field',
            required=True,
            options=options
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'select',
            'required',
            'id="id_select-field"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

        for option in options:
            self.assertIn(option[0], form.as_ul())
            self.assertIn(option[1], form.as_ul())

    def test_render_checkbox_group(self):
        manager = FieldManager()

        options = [
            ('option 1', 'Option 1'),
            ('option 2', 'Option 2'),
            ('option 3', 'Option 3'),
        ]

        manager.create(
            name='checkbox-group',
            field_type=Field.FIELD_CHECKBOX_GROUP,
            label='my checkobox group',
            required=True,
            options=options
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'checkbox',
            'required',
            'id="id_checkbox-group"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

        for option in options:
            self.assertIn(option[0], form.as_ul())
            self.assertIn(option[1], form.as_ul())

    def test_render_radio_group(self):
        manager = FieldManager()

        options = [
            ('option 1', 'Option 1'),
            ('option 2', 'Option 2'),
            ('option 3', 'Option 3'),
        ]

        manager.create(
            name='radio-group',
            field_type=Field.FIELD_RADIO_GROUP,
            label='my radio group',
            required=True,
            options=options
        )

        form = KanuForm(field_manager=manager)

        expected_content = [
            'radio',
            'required',
            'id="id_radio-group"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

        for option in options:
            self.assertIn(option[0], form.as_ul())
            self.assertIn(option[1], form.as_ul())
