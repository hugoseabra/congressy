from django.utils.functional import curry


class ModelHelperMixin(object):
    """Adds get_<field>_help_text into every field in model"""

    def _get_help_text(self, field_name):
        """Given a field name, return it's help text."""
        for field in self._meta.fields:
            if field.name == field_name:
                return field.help_text

    # noinspection PyArgumentList
    def __init__(self, *args, **kwargs):
        # Call the superclass first; it'll create all of the field objects.
        # noinspection PyArgumentList
        super(ModelHelperMixin, self).__init__(*args, **kwargs)

        # Again, iterate over all of our field objects.
        for field in self._meta.fields:
            # Create a string, get_FIELDNAME_help text
            method_name = "get_{0}_help_text".format(field.name)

            # We can use curry to create the method with a pre-defined argument
            curried_method = curry(self._get_help_text, field_name=field.name)

            # And we add this method to the instance of the class.
            setattr(self, method_name, curried_method)
