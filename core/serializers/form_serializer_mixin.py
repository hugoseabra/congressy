from copy import copy

from django.db.models import Model
from django.forms.models import model_to_dict
from rest_framework import serializers
from rest_framework.fields import empty


class FormSerializerMixin(object):
    class Meta:
        form = None

    def __init__(self, *args, **kwargs):
        self.instance = None
        self.form_instance = None
        super().__init__(*args, **kwargs)

    def run_validation(self, data=empty):
        return super().run_validation(data=self.partial_update_data(data))

    def partial_update_data(self, data=empty):
        if self.partial is False or not self.instance or data is empty:
            return data

        data = copy(data)

        for k, v in model_to_dict(self.instance).items():
            if k not in data:
                data[k] = v

        return data

    def validate(self, data):

        form_data = data

        for name, item in form_data.items():
            if isinstance(item, Model):
                form_data[name] = item.pk

        self.form_instance = self.get_form(data=form_data)

        if not self.form_instance.is_valid():
            raise serializers.ValidationError(
                {'errors': self.form_instance.errors}
            )
        else:
            cleaned_data = self.form_instance.cleaned_data

        return cleaned_data

    def get_form(self, data=None, **kwargs):
        """
        Returns an instance of the form to be used in this view.
        """

        assert hasattr(self, 'Meta'), (
            'Class {form_serializer_class} missing '
            '"Meta" class'.format(
                form_serializer_class=self.__class__.__name__
            )
        )

        assert hasattr(self.Meta, 'form'), (
            'Class {form_serializer_class} missing '
            '"Meta.form" attribute'.format(
                form_serializer_class=self.__class__.__name__
            )
        )

        if self.instance:
            kwargs['instance'] = self.instance

        if not self.form_instance:
            self.form_instance = self.Meta.form(data=data, **kwargs)

        return self.form_instance

    def save(self, **_):
        assert self.form_instance is not None
        self.instance = self.form_instance.save(True)
        return self.instance
