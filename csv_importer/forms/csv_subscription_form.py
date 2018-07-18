from django import forms
from django.db.models import Q
from kanu_locations.models import City

from core.util.string import clear_string

from gatheros_event.forms import PersonForm
from gatheros_subscription.forms import SubscriptionForm
from gatheros_subscription.models import Subscription


class CPFField(forms.CharField):

    def to_python(self, value):
        return clear_string(value)


class CNPJField(forms.CharField):

    def to_python(self, value):
        return clear_string(value)


class PhoneField(forms.CharField):

    def to_python(self, value):
        return clear_string(value)


class CSVSubscriptionForm(forms.Form):
    """
        Esse form é responsavel para processar os dados de uma linha de um
        arquivo CSV, dados os quais serão usados para gerar uma inscrição

        @TODO: Adicionar suporte a telefones internacionais
        @TODO: Adicionar suporte a endereços internacionais

    """

    lot_id = forms.IntegerField(required=True)
    name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    gender = forms.CharField()
    cpf = CPFField(max_length=11)
    phone = PhoneField(max_length=11)
    birth_date = forms.DateField(
        input_formats=[
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
        ]
    )
    street = forms.CharField(max_length=255)
    complement = forms.CharField(max_length=255)
    number = forms.CharField(max_length=255)
    village = forms.CharField(max_length=255)
    zip_code = forms.CharField(max_length=8)
    uf = forms.CharField(max_length=2)
    city = forms.CharField(max_length=255)
    institution = forms.CharField(max_length=255)
    institution_cnpj = forms.CharField(max_length=14)
    institution_function = forms.CharField(max_length=255)

    def __init__(self, event, user, *args, **kwargs):
        self.event = event
        self.user = user
        self.person_form = None
        self.subscription_form = None

        super().__init__(*args, **kwargs)



    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            return gender

        return str(gender).upper()

    def clean_uf(self):
        cleaned_uf = self.cleaned_data.get("uf")
        if not cleaned_uf:
            return cleaned_uf

        return str(cleaned_uf).upper()

    def clean_city(self):
        cleaned_city = self.cleaned_data.get('city')
        if not cleaned_city:
            return cleaned_city

        cleaned_uf = self.cleaned_data.get('uf')
        city_qs = City.objects.filter(
            Q(name=str(cleaned_city).upper()) |
            Q(name_ascii_=str(cleaned_city).upper())
        )
        if cleaned_uf:
            city_qs.filter(uf=cleaned_uf)

        if city_qs.count() == 0:
            raise forms.ValidationError(
                'Não foram encontradas cidades com este nome'
            )

        if city_qs.count() > 1:
            raise forms.ValidationError(
                'Foram encontradas mais de uma cidade com o mesmo nome'
            )

        return city_qs.first()

    def clean(self):
        """
            Aqui é feito a agregação dos dados para seus respectivos forms:

                - Dados de pessoas são entregues a um PersonForm e qualquer
                  erro gerador por esse form é repassado para esse form
                  
                - Dados de inscrição são entregues para um SubscriptionForm e
                  qualquer erro gerador por esse form é repassado para esse form

        """
        cleaned_data = super().clean()

        person_form = PersonForm(
            data={
                'name': cleaned_data.get('name'),
                'email': cleaned_data.get('email'),
                'gender': cleaned_data.get('gender'),
                'street': cleaned_data.get('street'),
                'complement': cleaned_data.get('complement'),
                'number': cleaned_data.get('number'),
                'village': cleaned_data.get('village'),
                'city': cleaned_data.get('city'),
                'country': 'br',
                'phone': cleaned_data.get('phone'),
                'cpf': cleaned_data.get('cpf'),
                'institution': cleaned_data.get('institution'),
                'institution_cnpj': cleaned_data.get('institution_cnpj'),
                'function': cleaned_data.get('institution_function'),
            }
        )

        if not person_form.is_valid():
            error_msgs = []
            for field, errs in person_form.items():
                error_msgs.append(str(errs))

            raise forms.ValidationError(
                'Dados de pessoa não válidos:'
                ' {}'.format("".join(error_msgs))
            )

        person = person_form.save(commit=False)

        subscription_form = SubscriptionForm(
            event=self.event,
            data={
                'person': person,
                'lot': cleaned_data.get('lot_id'),
                'origin': Subscription.DEVICE_ORIGIN_CSV_IMPORT,
                'created_by': self.user.pk,
            }
        )

        if not subscription_form.is_valid():
            error_msgs = []
            for field, errs in subscription_form.items():
                error_msgs.append(str(errs))

            raise forms.ValidationError(
                'Dados de inscrição não válidos:'
                ' {}'.format("".join(error_msgs))
            )

        self.person_form = person_form
        self.subscription_form = subscription_form

        return cleaned_data

    def save(self):
        if self.errors:
            raise ValueError(
                "Você não pode salvar dados de formulário inválido."
            )

        self.person_form.save()
        return self.subscription_form.save()
