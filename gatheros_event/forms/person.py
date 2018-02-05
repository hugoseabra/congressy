""" Formulários de `Person` """
from django import forms
from django.db.models.fields import NOT_PROVIDED
from django.utils import six
from kanu_locations.models import City

from gatheros_event.models import Person, Occupation


def create_years_list():
    years = []
    epoch = 1950
    for i in range(60):
        epoch += 1
        years.append(epoch)

    return years


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class DateInput(forms.TextInput):
    input_type = 'date'


class PersonForm(forms.ModelForm):
    """ Formulário de Person. """

    class Meta:
        """ Meta """
        model = Person
        # fields = '__all__'
        exclude = ('user', 'occupation')

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'cpf': TelephoneInput(),
            'name': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'me@you.com'}),
            'phone': TelephoneInput(attrs={'placeholder': '(00) 00000-0000'}),
            'zip_code': TelephoneInput(),
            'city': forms.HiddenInput()
        }

    def __init__(self, is_chrome=False, **kwargs):

        # if 'instance' in kwargs:
        #     self.instance = kwargs.get('instance')
        # else:
        #     self.instance = None
        #
        # if 'data' in kwargs:
        #     self.data = kwargs.get('data', {})
        # else:
        #     self.data = {}
        #
        # self.fill_blank_data_when_user()

        super().__init__(**kwargs)

        if is_chrome:
            self.fields['birth_date'].widget = DateInput()

        else:
            self.fields['birth_date'].widget = forms.SelectDateWidget(
                attrs=({'style': 'width: 30%; display: inline-block;'}),
                years=create_years_list(),
            )

    def setAsRequired(self, field_name):
        if field_name not in self.fields:
            return

        self.fields[field_name].required = True

    def clean_city(self):
        if 'city' not in self.data:
            return None

        return City.objects.get(pk=self.data['city'])

    def clean_email(self):
        return self.data['email'].lower()

    def clean_occupation(self):
        return Occupation.objects.get(pk=self.data['occupation'])

    def fill_blank_data_when_user(self):
        """
        When instance has user, the existing data must remain and the blank
        data must be filled.
        """
        if not self.instance:
            return

        if self.instance.user is None:
            return

        fields = [field for field in six.iterkeys(self.data)]

        for field_name in fields:
            incoming_value = self.data.get(field_name)

            # If incoming value is not blank
            if not incoming_value:
                continue

            # If field_name does exist in instance
            if not hasattr(self.instance, field_name):
                continue

            field = self.instance._meta.get_field(field_name)
            has_default = field.default != NOT_PROVIDED
            value = getattr(self.instance, field_name)

            # If value exists and it does not come from a default value
            if not value or (value and has_default):
                continue

            # Remain same value from persistence
            self.data[field_name] = value


# class PersonSubscribeForm(forms.ModelForm):
#     """ Formulário de Person. """
#
#     class Meta:
#         """ Meta """
#         model = Person
#         exclude = ('user', 'occupation')
#
#         widgets = {
#             # CPF como telefone para aparecer como número no mobile
#             'cpf': TelephoneInput(),
#             'name': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
#             'email': forms.EmailInput(attrs={'placeholder': 'me@you.com'}),
#             'phone': TelephoneInput(attrs={'placeholder': '(00) 00000-0000'}),
#             'zip_code': TelephoneInput(),
#             'city': forms.HiddenInput()
#         }
#
#     def __init__(self, is_chrome=False, **kwargs):
#
#         super().__init__(**kwargs)
#
#         self.fields['transaction_type'] = forms.CharField(
#             max_length=50,
#             widget=forms.HiddenInput(),
#         )
#
#         self.fields['card_hash'] = forms.CharField(
#             widget=forms.HiddenInput(),
#             required=False,
#         )
#
#         self.fields['amount'] = forms.IntegerField(
#             widget=forms.HiddenInput(),
#         )
#
#         self.fields['organization'] = forms.IntegerField(
#             widget=forms.HiddenInput(),
#         )
#
#         if is_chrome:
#             self.fields['birth_date'].widget = DateInput()
#         else:
#
#             self.fields['birth_date'].widget = forms.SelectDateWidget(
#                 attrs=({'style': 'width: 30%; display: inline-block;'}),
#                 years=create_years_list(),
#             )
#
#     def setAsRequired(self, field_name):
#         if field_name not in self.fields:
#             return
#
#         self.fields[field_name].required = True
#
#     def clean_city(self):
#         if 'city' not in self.data:
#             return None
#
#         return City.objects.get(pk=self.data['city'])
#
#     def clean_email(self):
#         return self.data['email'].lower()
#
#     def clean_occupation(self):
#         return Occupation.objects.get(pk=self.data['occupation'])
#
#     def clean_phone(self):
#         phone = self.data['phone']
#         phone = phone.replace(" ", "").replace('(', '').replace(')', '').replace('-', '')
#         return phone
#
#     def fill_blank_data_when_user(self):
#         """
#         When instance has user, the existing data must remain and the blank
#         data must be filled.
#         """
#         if not self.instance:
#             return
#
#         if self.instance.user is None:
#             return
#
#         fields = [field for field in six.iterkeys(self.data)]
#
#         for field_name in fields:
#             incoming_value = self.data.get(field_name)
#
#             # If incoming value is not blank
#             if not incoming_value:
#                 continue
#
#             # If field_name does exist in instance
#             if not hasattr(self.instance, field_name):
#                 continue
#
#             field = self.instance._meta.get_field(field_name)
#             has_default = field.default != NOT_PROVIDED
#             value = getattr(self.instance, field_name)
#
#             # If value exists and it does not come from a default value
#             if not value or (value and has_default):
#                 continue
#
#             # Remain same value from persistence
#             self.data[field_name] = value
#
#     def clean(self):
#
#         cleaned_data = super(PersonSubscribeForm, self).clean()
#
#         organization = Organization.objects.get(pk=cleaned_data['organization'])
#
#         if cleaned_data['transaction_type']:
#
#             if not cleaned_data['amount']:
#                 self.add_error(None, ValidationError('Não foi possivel completar sua inscrição no momento.'))
#
#             if cleaned_data['transaction_type'] == 'credit_card':
#
#                 transaction_instance_data = {
#                     "price": cleaned_data['amount'],
#                     "card_hash": cleaned_data['card_hash'],
#                     "customer": {
#                         "name": cleaned_data['name'],
#                         "type": "individual",
#                         "country": "br",
#                         "email": cleaned_data['email'],
#                         "documents": [
#                             {
#                                 "type": "cpf",
#                                 "number": cleaned_data['cpf'],
#                             }
#                         ],
#                         "phone_numbers": ["+55" + cleaned_data['phone']],
#                         "birthday": cleaned_data['birth_date'].strftime('%Y-%d-%m'),
#                     },
#
#                     "billing": {
#                         "name": cleaned_data['name'],
#                         "address": {
#                             "country": "br",
#                             "state": cleaned_data['city'].uf.lower(),
#                             "city": cleaned_data['city'].name.lower().capitalize(),
#                             "neighborhood": cleaned_data['village'],
#                             "street": cleaned_data['street'],
#                             "street_number": cleaned_data['number'],
#                             "zipcode": cleaned_data['zip_code']
#                         }
#                     },
#
#                     "event_name": organization.name,
#                     'recipient_id': organization.recipient_id,
#                 }
#                 trx = create_credit_card_transaction(transaction_instance_data)
#
#             elif cleaned_data['transaction_type'] == 'boleto':
#
#                 transaction_instance_data = {
#
#                     "price": cleaned_data['amount'],
#
#                     "customer": {
#                         "name": cleaned_data['name'],
#                         "type": "individual",
#                         "country": "br",
#                         "email": cleaned_data['email'],
#                         "documents": [
#                             {
#                                 "type": "cpf",
#                                 "number": cleaned_data['cpf'],
#                             }
#                         ],
#                         "phone_numbers": [
#                             "+55" + cleaned_data['phone'].replace(" ", "").replace('(', '').replace(')',
#                                                                                                          '').replace(
#                                 '-', '')],
#                         "birthday": cleaned_data['birth_date'].strftime('%Y-%m-%d'),
#                     },
#
#                     "billing": {
#                         "name": cleaned_data['name'],
#                         "address": {
#                             "country": "br",
#                             "state": cleaned_data['city'].uf.lower(),
#                             "city": cleaned_data['city'].name.lower().capitalize(),
#                             "neighborhood": cleaned_data['village'],
#                             "street": cleaned_data['street'],
#                             "street_number": cleaned_data['number'],
#                             "zipcode": cleaned_data['zip_code']
#                         }
#                     },
#
#                     "event_name": organization.name,
#
#                     'recipient_id': organization.recipient_id,
#                 }
#                 trx = create_boleto_transaction(transaction_instance_data)
#
#             api_result_type = None
#
#             try:
#                 api_result_type = trx[0]['type']
#             except KeyError:
#                 pass
#
#             if api_result_type:
#                     self.add_error(None, ValidationError('Não foi possivel completar sua inscrição neste momento.'))
#             else:
#
#                 transaction = Transaction(
#                     id=trx['id']
#                 )
#
#                 transaction.save()
#
#         return cleaned_data
