from django import forms
from django.contrib import messages
from django.utils import six

# TODO add test and documentation


class CombinedFormBase(forms.Form):
    form_classes = {}
    instances = {}

    messages = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, form_class in six.iteritems(self.form_classes):
            # kwargs.update({'prefix': name})
            form = form_class(*args, **kwargs)
            setattr(self, name, form)
            self.fields.update(form.fields)
            self.initial.update(form.initial)

    def is_valid(self):
        isValid = True
        for name in self.form_classes.keys():
            form = getattr(self, name)

            if not form.is_valid():
                isValid = False

        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        if not super().is_valid():
            isValid = False

        for name in self.form_classes.keys():
            form = getattr(self, name)
            self.errors.update(form.errors)

        return isValid

    def clean(self):
        cleaned_data = super().clean()
        for name in self.form_classes.keys():
            form = getattr(self, name)
            cleaned_data.update(form.cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        return self.save_all(commit=commit)

    def save_all(self, commit=True):
        for name in self.form_classes.keys():
            form = getattr(self, name)
            self.instances[name] = form.save(commit)

        return self.instances
