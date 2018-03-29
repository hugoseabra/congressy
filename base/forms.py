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

        self._check_form_classes()
        self.form_instances = self._get_form_instances(**kwargs)

        self.instances = kwargs.get('instances', {})
        if self.instances:
            del kwargs['instances']

        super().__init__(data=data, files=files, auto_id=auto_id,
                         prefix=prefix, initial=initial,
                         error_class=error_class, label_suffix=label_suffix,
                         empty_permitted=empty_permitted,
                         field_order=field_order,
                         use_required_attribute=use_required_attribute,
                         renderer=renderer)

        for form_name, form in six.iteritems(self.form_instances):
            self.fields.update(form.fields)

    def is_valid(self):
        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        super().is_valid()

        valid = True
        for form_name, form in self.form_instances.items():
            if not form.is_valid():
                valid = False
                self.errors.update(form.errors)

        return valid

    def clean(self):
        cleaned_data = super().clean()
        for form_name, form in self.form_instances.items():
            if hasattr(form, 'cleaned_data'):
                cleaned_data.update(form.cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        return self.save_all(commit=commit)

    def save_all(self, commit=True):
        for form_name, form in self.form_instances.items():
            if not callable(form.save):
                raise Exception(
                    'O formulário "{}" não possui o método save().'.format(
                        form_name
                    )
                )

            self.instances[form_name] = form.save(commit=commit)

        return self.instances

    def _get_form_instances(self, **kwargs) -> dict:
        """
            Recupera lista de instâncias das classes em "form_classes"
            configuradas.
        """
        self._check_instances(**kwargs)

        form_instances = {}
        for item in self.form_classes:
            name = item[0]
            form_class = item[1]

            display_fields = self.display_fields.get(name)
            hidden_fields = self.hidden_fields.get(name)

            if display_fields:
                # Se o formulário for um ApplicationServiceMixin, ele
                # suportará display_fields diretamente.
                form_class.display_fields = display_fields

            if hidden_fields:
                # Se o formulário for um ApplicationServiceMixin, ele
                # suportará hidden_fields diretamente.
                form_class.hidden_fields = hidden_fields

            form_kwargs = kwargs.copy()
            # form_kwargs.update({'prefix': name})

            if name in self.instances:
                form_kwargs.update({'instance': self.instances.get(name)})

            form = form_class(**form_kwargs)

            if display_fields:
                self._configure_form_fields(form, display_fields)

            form_instances[name] = form

        return form_instances

    def _check_form_classes(self):
        """
            Verifica se "form_classes" configurado é um tuple de tuples com
            dois índices.
        """
        if not isinstance(self.form_classes, tuple):
            raise Exception(
                '"form_classes" deve ser configurado com um tuple de tuples.'
            )

        for item in self.form_classes:
            if not isinstance(item, tuple) or len(item) != 2:
                raise Exception(
                    'Cada item de "form_classes" deve ser um tuple de dois'
                    ' índices.'
                )

    def _check_instances(self, **kwargs):
        """
            Verifica se "instance" é passado no kwargs.
        """
        if 'instance' in kwargs:
            raise Exception(
                'Você deve informar "instances" como um dict(). O parâmetro'
                ' "instance" não é usada em "CombinedFormBase".'
            )

        if 'instances' in kwargs:
            instances = kwargs.get('instances', {})

            if not isinstance(instances, dict):
                raise Exception('Instances must be a dict().')

            for instances_key in instances.keys():
                if instances_key not in self.form_classes:
                    raise Exception(
                        'Você deve informar um dict() cujas chaves sejam'
                        ' as mesmas utilizadas em "form_classes".'
                    )

    def _configure_form_fields(self, form, display_fields):
        """
            Configura campos a serem exibidos no formulário.
        """
        self._check_display_fields(form, display_fields)

        new_fields = OrderedDict()
        for field_name, field in six.iteritems(form.fields):
            if field_name in display_fields:
                new_fields[field_name] = field

        form.fields = new_fields

    def _check_display_fields(self, form, display_fields):
        """
        Valida se o formulário possui todos os campos da lista de campos a
        exibir.
        """
        field_names = form.fields.keys()

        for field_name in display_fields:
            if field_name in field_names:
                continue

            raise Exception(
                'O formulário "{}" não possui o campo'
                ' "{}". As opções são: {}'.format(
                    form.__class__,
                    field_name,
                    ', '.join(field_names)
                )
            )
