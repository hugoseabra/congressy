from django import forms

from addon import services, models
from core.forms.widgets import SplitDateTimeWidget


class OptionalForm(forms.Form):
    """ Formulário Genérico de opcional. """

    optional_kind = forms.ChoiceField(
        choices=(
            ('service', 'Serviço'),
            ('product', 'Produto'),
        ),
        widget=forms.Select,
        label='Ofertar como',
    )
    optional_product_type = forms.ModelChoiceField(
        queryset=models.OptionalProductType.objects.get_queryset(),
        widget=forms.Select,
        label='Tipo',
        required=False,
    )
    optional_service_type = forms.ModelChoiceField(
        queryset=models.OptionalServiceType.objects.get_queryset(),
        widget=forms.Select,
        label='Tipo',
        required=False,
    )
    schedule_start = forms.DateTimeField(
        widget=SplitDateTimeWidget,
        label='Programação - início',
        required=False,
    )

    schedule_end = forms.DateTimeField(
        widget=SplitDateTimeWidget,
        label='Programação - fim',
        required=False,
    )

    theme = forms.ChoiceField(
        widget=forms.Select,
        label='Tema',
        required=False,
    )

    def __init__(self, user, event, instance=None, *args, **kwargs):
        self.instance = instance
        self.user = user
        self.event = event

        super().__init__(*args, **kwargs)

        # Opcional de serviço possui todos os campos de produto + os campos
        # de serviço. Vamos exibir todos os campos e gerenciar a exibição
        # deles dinamicamente.
        service_service = services.ServiceService(event=event)

        ignore_fields = [
            'optional_type',
            'created_by',
            'modified_by',
            'schedule_start',
            'schedule_end',
            'theme',
        ]

        for f_name, field in service_service.manager.fields.items():
            if f_name in ignore_fields:
                continue
            self.fields.update({f_name: field})

        self.fields['description'].widget.attrs.update({'rows': 3})

        theme_choices = [('', '---------')]
        theme_choices += [
            (t.pk, t.name) for t in models.Theme.objects.filter(event=event)
        ]
        self.fields['theme'].choices = theme_choices

    def save(self):

        author = '{} ({})'.format(self.user.get_full_name(), self.user.email),

        date_end_sub = self.cleaned_data.get('date_end_sub')
        date_end_sub_0 = date_end_sub.strftime('%d/%m/%Y')
        date_end_sub_1 = date_end_sub.strftime('%H:%M')

        data = {
            'lot_category': self.cleaned_data.get('lot_category').pk,
            'name': self.cleaned_data.get('name'),
            'date_end_sub_0': date_end_sub_0,
            'date_end_sub_1': date_end_sub_1,
            'published': False,
            'price': self.cleaned_data.get('price'),
            'restrict_unique': self.cleaned_data.get('restrict_unique'),
            'description': self.cleaned_data.get('description'),
            'modified_by': author,
            'created_by': author
        }

        kind = self.cleaned_data.get('optional_kind')
        if kind == 'service':
            data['optional_type'] = \
                self.cleaned_data.get('optional_service_type').pk

            dt_start = self.cleaned_data.get('schedule_start')
            dt_end = self.cleaned_data.get('schedule_end')

            data['theme'] = self.cleaned_data.get('theme')
            data['schedule_start_0'] = dt_start.strftime('%d/%m/%Y')
            data['schedule_start_1'] = dt_start.strftime('%H:%M')
            data['schedule_end_0'] = dt_end.strftime('%d/%m/%Y')
            data['schedule_end_1'] = dt_end.strftime('%H:%M')

            service_class = services.ServiceService

        elif kind == 'product':
            data['optional_type'] = \
                self.cleaned_data.get('optional_product_type').pk

            service_class = services.ProductService

        else:
            raise Exception(
                'Opcional deve ser informado como "product" ou "service".'
            )

        kwargs = {
            'instance': self.instance,
            'data': data,
        }

        service = service_class(event=self.event, **kwargs)

        if not service.is_valid():
            print(service.errors)
            raise Exception('serviço com dados inválidos.')

        return service.save()
