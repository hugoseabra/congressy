from django import forms
from django.db import transaction
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


class ZipCodeField(forms.CharField):

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

    lot_id = forms.IntegerField()
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    gender = forms.CharField(max_length=50)
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
    zip_code = ZipCodeField(max_length=8)
    uf = forms.CharField(max_length=100)
    city = forms.CharField(max_length=255)
    institution = forms.CharField(max_length=255)
    institution_cnpj = CNPJField(max_length=14)
    function = forms.CharField(max_length=255)

    def __init__(self, event, user, required_keys: list, *args, **kwargs):

        self.required_keys = required_keys
        self.event = event
        self.user = user
        self.person_form = None
        self.subscription_form = None

        super().__init__(*args, **kwargs)

        for field in self.fields:

            if field in required_keys:
                self.set_as_required(field)
            else:
                self.set_as_not_required(field)

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            return gender

        gender = str(gender).lower()

        if gender == "feminino":
            gender = 'f'
        elif gender == "masculino":
            gender = 'm'

        if len(str(gender)) > 1:
            raise forms.ValidationError("Sexo deve ser apenas uma letra")

        return gender.upper()

    def clean_uf(self):
        cleaned_uf = self.cleaned_data.get("uf")
        if not cleaned_uf:
            return cleaned_uf

        if len(str(cleaned_uf)) > 2:
            raise forms.ValidationError(
                "Estados devem ser informados em forma de sigla.")

        return str(cleaned_uf).upper()

    def clean_city(self):
        cleaned_city = self.cleaned_data.get('city')
        if not cleaned_city:
            return cleaned_city

        cleaned_uf = self.cleaned_data.get('uf')

        city_qs = City. objects.filter(
            Q(name=str(cleaned_city).upper()) |
            Q(name_ascii=str(cleaned_city).upper())
        )
        
        if cleaned_uf:
            city_qs = city_qs.filter(uf=cleaned_uf)

        if city_qs.count() > 1:
            raise forms.ValidationError(
                'Foram encontradas mais de uma cidade com o mesmo nome'
            )

        if city_qs.count() == 1:
            return city_qs.first().pk

        if city_qs.count() == 0:

            # Busca por pk de city
            found_city = None
            try:
                city_pk = int(cleaned_city)
                found_city = City.objects.get(pk=city_pk).pk
            except (ValueError, City.DoesNotExist):
                pass

            if found_city:
                return found_city

        raise forms.ValidationError(
            'Não foram encontradas cidades com este nome'
        )

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
                'country': 'BR',
                'phone': cleaned_data.get('phone'),
                'cpf': cleaned_data.get('cpf'),
                'institution': cleaned_data.get('institution'),
                'institution_cnpj': cleaned_data.get('institution_cnpj'),
                'function': cleaned_data.get('institution_function'),
            }
        )

        if not person_form.is_valid():

            for field, errs in person_form.errors.items():
                if field not in self.fields:
                    raise Exception(
                        "Field({}) não existe em formulario de pessoa".format(
                            field))

                raise forms.ValidationError({field: [errs[0], ]})

        # Dry run.
        with transaction.atomic():

            person = person_form.save()

            subscription_form = SubscriptionForm(
                event=self.event,
                data={
                    'person': person.pk,
                    'lot': cleaned_data.get('lot_id'),
                    'origin': Subscription.DEVICE_ORIGIN_CSV_IMPORT,
                    'created_by': self.user.pk,
                }
            )

            if not subscription_form.is_valid():
                error_msgs = []
                for field, errs in subscription_form.errors.items():
                    for err in errs:
                        error_msgs.append('{}: {}'.format(field, err))

                raise Exception(
                    'Dados de inscrição não válidos:'
                    ' {}'.format("".join(error_msgs))
                )

            self.person_form = person_form
            self.subscription_form = subscription_form
            transaction.set_rollback(True)

        return cleaned_data

    def save(self):
        if self.errors:
            raise ValueError(
                "Você não pode salvar dados de formulário inválido."
            )

        self.person_form.save()

        subscription = self.subscription_form.save()
        subscription.completed = True
        subscription.status = Subscription.CONFIRMED_STATUS
        subscription.origin = Subscription.DEVICE_ORIGIN_CSV_IMPORT
        return subscription.save()

    def set_as_required(self, field_name):

        if field_name not in self.fields:
            raise ValueError('Unknown field name: {}'.format(field_name))
        self.fields[field_name].required = True

    def set_as_not_required(self, field_name):

        if field_name not in self.fields:
            raise ValueError('Unknown field name: {}'.format(field_name))
        self.fields[field_name].required = False
