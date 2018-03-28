from django import forms
from django.forms.utils import ErrorList
from django.utils import six
from django.utils.datastructures import OrderedDict


# TODO add test and documentation


class CombinedFormBase(forms.Form):
    form_classes = ()
    display_fields = {}
    hidden_fields = {}
    instances = {}

    messages = {}

    def __init__(self, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        auto_id = kwargs.get('auto_id', 'id_%s')
        prefix = kwargs.get('prefix')
        initial = kwargs.get('initial', {})
        error_class = kwargs.get('error_class', ErrorList)
        label_suffix = kwargs.get('label_suffix')
        empty_permitted = kwargs.get('empty_permitted', False)
        field_order = kwargs.get('field_order')
        use_required_attribute = kwargs.get('use_required_attribute')
        renderer = kwargs.get('renderer')

        if 'instance' in kwargs:
            raise Exception(
                'You must provide instances as a dict(). Instance will not be'
                ' used in Application Service.'
            )

        if 'instances' in kwargs:
            self.instances = kwargs.get('instances', {})

            if not isinstance(self.instances, dict):
                raise Exception('Instances must be a dict().')

            del kwargs['instances']

        form_instances = []
        for item in self.form_classes:
            name = item[0]
            form_class = item[1]

            display_fields = self.display_fields.get(name)
            hidden_fields = self.hidden_fields.get(name)

            if display_fields:
                form_class.display_fields = display_fields

            if hidden_fields:
                form_class.hidden_fields = hidden_fields

            form_kwargs = kwargs.copy()
            # form_kwargs.update({'prefix': name})

            if name in self.instances:
                form_kwargs.update({'instance': self.instances.get(name)})

            form = form_class(**form_kwargs)

            if display_fields:
                field_names = form.fields.keys()

                for field_name in display_fields:
                    if field_name not in field_names:
                        raise Exception(
                            'O formulário "{}" não possui o campo'
                            ' "{}". As opções são: {}'.format(
                                form_class,
                                field_name,
                                ', '.join(field_names)
                            )
                        )

                new_fields = OrderedDict()
                for field_name, field in six.iteritems(form.fields):
                    if field_name in display_fields:
                        new_fields[field_name] = field

                form.fields = new_fields

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
        for item in self.form_classes:
            name = item[0]

            form = getattr(self, name)

            if not form.is_valid():
                isValid = False

        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        super().is_valid()

        for item in self.form_classes:
            name = item[0]
            form = getattr(self, name)
            self.errors.update(form.errors)

        return isValid

    def clean(self):
        cleaned_data = super().clean()
        for item in self.form_classes:
            name = item[0]
            form = getattr(self, name)
            if hasattr(form, 'cleaned_data'):
                cleaned_data.update(form.cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        return self.save_all(commit=commit)

    def save_all(self, commit=True):
        for item in self.form_classes:
            name = item[0]
            form = getattr(self, name)
            self.instances[name] = form.save(commit=commit)

        return self.instances
