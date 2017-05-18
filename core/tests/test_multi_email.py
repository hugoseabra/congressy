"""Simple Test of multi-email"""

from django.test import SimpleTestCase
from django.core.exceptions import ValidationError

from core.fields import MultiEmailField as MultiEmailFormField
from core.widgets import MultiEmailWidget


class MultiEmailFormFieldTest(SimpleTestCase):
    """MultiEmailFormFieldTest class"""

    def test__widget(self):
        """Tests widget instance"""

        field = MultiEmailFormField()
        self.assertIsInstance(field.widget, MultiEmailWidget)

    def test__to_python(self):
        """Tests to_python() method"""

        field = MultiEmailFormField()
        # Empty values
        for val in ['', None]:
            self.assertEquals([], field.to_python(val))
        # One line correct value
        val = '  foo@bar.com    '
        self.assertEquals(['foo@bar.com'], field.to_python(val))
        # Multi lines correct values (test of #0010614)
        val = 'foo@bar.com\nfoo2@bar2.com\r\nfoo3@bar3.com'
        self.assertEquals(
            ['foo@bar.com', 'foo2@bar2.com', 'foo3@bar3.com'],
            field.to_python(val)
        )

    def test__validate(self):
        """Tests field validation in widget"""

        field = MultiEmailFormField(required=True)
        # Empty value
        val = []
        self.assertRaises(ValidationError, field.validate, val)
        # Incorrect value
        val = ['not-an-email.com']
        self.assertRaises(ValidationError, field.validate, val)
        # An incorrect value with correct values
        val = ['foo@bar.com', 'not-an-email.com', 'foo3@bar3.com']
        self.assertRaises(ValidationError, field.validate, val)
        # Should not happen (to_python do the strip)
        val = ['  foo@bar.com    ']
        self.assertRaises(ValidationError, field.validate, val)
        # Correct value
        val = ['foo@bar.com']
        field.validate(val)


class MultiEmailWidgetTest(SimpleTestCase):
    """MultiEmailWidgetTest class"""

    def test__prep_value__empty(self):
        """Tests if Widget empty value is really empty"""
        widget = MultiEmailWidget()
        value = widget.prep_value('')
        self.assertEqual(value, '')

    def test__prep_value__string(self):
        """Test if Widget value string is equals the given string"""

        widget = MultiEmailWidget()
        value = widget.prep_value('foo@foo.fr\nbar@bar.fr')
        self.assertEqual(value, 'foo@foo.fr\nbar@bar.fr')

    def test__prep_value__list(self):
        """Test if Widget value list is equals the given list"""

        widget = MultiEmailWidget()
        value = widget.prep_value(['foo@foo.fr', 'bar@bar.fr'])
        self.assertEqual(value, 'foo@foo.fr\nbar@bar.fr')

    def test__prep_value__raise(self):
        """Test raises Widget value preparation"""

        widget = MultiEmailWidget()
        self.assertRaises(ValidationError, widget.prep_value, 42)
