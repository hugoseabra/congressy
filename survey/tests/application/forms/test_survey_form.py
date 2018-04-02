from django.test import TestCase

from survey.forms.field import SurveyField
from survey.forms.survey import SurveyForm
from survey.tests import MockFactory
from survey.models import Answer


class SurveyFormTest(TestCase):
    """ Testa renderização de campos do formulário dinâmico. """

    def setUp(self):
        fake_factory = MockFactory()
        self.survey = fake_factory.fake_survey()
        self.user = fake_factory.fake_user()
        self.question = fake_factory.fake_question(survey=self.survey)
        self.author = fake_factory.fake_author(survey=self.survey,
                                               user=self.user)
        self.anon_author = fake_factory.fake_author(survey=self.survey)

        self.answer = fake_factory.fake_answer(question=self.question,
                                               author=self.author)
        self.non_authored_answer = fake_factory.fake_answer(
            question=self.question,
            author=self.anon_author)

    def test_render_input_text(self):
        """ Renderização de campo INPUT_TEXT. """
        data = {
            'name': 'name',
            'field_type': SurveyField.FIELD_INPUT_TEXT,
            'label': 'nome',
            'required': True,
            'max_length': 10,
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

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
        """ Renderização de campo INPUT_NUMBER. """
        data = {
            'name': 'name',
            'field_type': SurveyField.FIELD_INPUT_NUMBER,
            'label': 'nome',
            'required': True,
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'input',
            'type="number"',
            'required',
            'id="id_name"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_date(self):
        """ Renderização de campo INPUT_DATE. """
        data = {
            'name': 'some_date',
            'field_type': SurveyField.FIELD_INPUT_DATE,
            'label': 'date',
            'required': True,
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'input',
            'type="date"',
            'required',
            'id="id_some_date"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_datetime(self):
        """ Renderização de campo INPUT_DATETIME. """
        data = {
            'name': 'some_datetime',
            'field_type': SurveyField.FIELD_INPUT_DATETIME,
            'label': 'datetime',
            'required': True
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'input',
            'type="datetime-local"',
            'required',
            'id="id_some_datetime"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_email(self):
        """ Renderização de campo INPUT_EMAIL. """
        data = {
            'name': 'some_email',
            'field_type': SurveyField.FIELD_INPUT_EMAIL,
            'label': 'e-mail',
            'required': True
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'input',
            'type="email"',
            'required',
            'id="id_some_email"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_input_tel(self):
        """ Renderização de campo INPUT_TEL. """
        data = {
            'name': 'some_tel',
            'field_type': SurveyField.FIELD_INPUT_PHONE,
            'label': 'celular',
            'required': True
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

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
        """ Renderização de campo TEXTAREA. """
        data = {
            'name': 'textarea_example',
            'field_type': SurveyField.FIELD_TEXTAREA,
            'label': 'my textarea',
            'required': True
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

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
        """ Renderização de campo BOOLEAN. """
        data = {
            'name': 'boolean-field',
            'field_type': SurveyField.FIELD_BOOLEAN,
            'label': 'my boolean field',
            'required': True
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'input',
            'type="checkbox"',
            'id="id_boolean-field"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

    def test_render_select(self):
        """ Renderização de campo SELECT. """

        options = [
            ('option 1', 'Option 1'),
            ('option 2', 'Option 2'),
            ('option 3', 'Option 3'),
        ]

        data = {
            'name': 'select-field',
            'field_type': SurveyField.FIELD_SELECT,
            'label': 'my select field',
            'required': True,
            'options': options
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

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
        """ Renderização de campo CHECKBOX_GROUP. """
        options = [
            ('option 1', 'Option 1'),
            ('option 2', 'Option 2'),
            ('option 3', 'Option 3'),
        ]

        data = {
            'name': 'checkbox-group',
            'field_type': SurveyField.FIELD_CHECKBOX_GROUP,
            'label': 'my checkobox group',
            'options': options
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'checkbox',
            'id="id_checkbox-group"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

        for option in options:
            self.assertIn(option[0], form.as_ul())
            self.assertIn(option[1], form.as_ul())

    def test_render_radio_group(self):
        """ Renderização de campo RADIO_GROUP. """
        options = [
            ('option 1', 'Option 1'),
            ('option 2', 'Option 2'),
            ('option 3', 'Option 3'),
        ]

        data = {
            'name': 'radio-group',
            'field_type': SurveyField.FIELD_RADIO_GROUP,
            'label': 'my radio group',
            'options': options
        }

        form = SurveyForm(survey=self.survey)
        form.create_field(question=self.question, **data)

        expected_content = [
            'radio',
            'id="id_radio-group"',
        ]

        for part in expected_content:
            self.assertIn(part, form.as_ul())

        for option in options:
            self.assertIn(option[0], form.as_ul())
            self.assertIn(option[1], form.as_ul())

    def test_save_new_answer(self):
        """
            Testa a persistencia sem passar um usuario.
        :return:
        """

        form = SurveyForm(survey=self.survey, data={
            self.question.name: '41'
        })

        self.assertTrue(form.is_valid())

        persisted_answer_list = form.save()

        self.assertEqual(len(persisted_answer_list), 1)
        self.assertNotEqual(persisted_answer_list[0].pk, self.answer.pk)

    def test_save_existing_answer(self):
        """
            Testa a persistencia passando um usuario.
        :return:
        """

        form = SurveyForm(survey=self.survey, user=self.user, data={
            self.question.name: '41'
        })

        self.assertTrue(form.is_valid())

        persisted_answer_list = form.save()

        self.assertEqual(len(persisted_answer_list), 1)
        self.assertEqual(persisted_answer_list[0].pk, self.answer.pk)
