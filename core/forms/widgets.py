from django import forms


class AjaxChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class DateInput(forms.TextInput):
    input_type = 'date'

