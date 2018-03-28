from django import forms
from django.forms.utils import ErrorList
from django.utils import six


# TODO add test and documentation


class CombinedFormBase(forms.Form):
    form_classes = {}
    instances = {}

    messages = {}

    def __init__(self, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        auto_id = kwargs.get('auto_id', 'id_%s')
        prefix = kwargs.get('prefix')
        initial = kwargs.get('initial')
        error_class = kwargs.get('error_class', ErrorList)
        label_suffix = kwargs.get('label_suffix')
        empty_permitted = kwargs.get('empty_permitted', False)
        field_order = kwargs.get('field_order')
        use_required_attribute = kwargs.get('use_required_attribute')
        renderer = kwargs.get('renderer')

        if 'instance' in kwargs:
            raise Exception(
                'You must provide instances as a dict(), not an only instance.'
            )

        if 'instances' in kwargs:
            self.instances = kwargs.get('instances', {})
            del kwargs['instances']

        form_instances = []
        for name, form_class in six.iteritems(self.form_classes):
            form_kwargs = kwargs.copy()
            # form_kwargs.update({'prefix': name})

            if name in self.instances:
                form_kwargs.update({'instance': self.instances.get(name)})

            form = form_class(**form_kwargs)
            form_instances.append(form)

            setattr(self, name, form)
            initial.update(form.initial)

        super().__init__(data=data, files=files, auto_id=auto_id,
                         prefix=prefix, initial=initial,
                         error_class=error_class, label_suffix=label_suffix,
                         empty_permitted=empty_permitted,
                         field_order=field_order,
                         use_required_attribute=use_required_attribute,
                         renderer=renderer)

        for form in form_instances:
            self.fields.update(form.fields)

    def is_valid(self):
        isValid = True
        for name in self.form_classes.keys():
            form = getattr(self, name)

            if not form.is_valid():
                isValid = False

        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        super().is_valid()

        for name in self.form_classes.keys():
            form = getattr(self, name)
            self.errors.update(form.errors)

        return isValid

    def clean(self):
        cleaned_data = super().clean()
        for name in self.form_classes.keys():
            form = getattr(self, name)
            if hasattr(form, 'cleaned_data'):
                cleaned_data.update(form.cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        return self.save_all(commit=commit)

    def save_all(self, commit=True):
        for name in self.form_classes.keys():
            form = getattr(self, name)
            self.instances[name] = form.save(commit=commit)

        return self.instances
