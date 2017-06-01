# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""
from django import forms
from django.contrib.auth import (
    password_validation,
)

from gatheros_event.models import Person


class ProfileForm(forms.ModelForm):
    """
    Pessoas que são usuários do sistema
    """
    error_messages = {
        'password_mismatch': "Os dois passwords não combinam",
    }
    new_password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label="Confirmar Senha",
        strip=False,
        widget=forms.PasswordInput
    )

    def __init__(self, user, instance=None, data=None, *args, **kwargs):
        super(ProfileForm, self).__init__(
            instance=instance,
            data=data,
            *args,
            **kwargs
        )
        self.user = user

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, **_):
        super(ProfileForm, self).save(commit=True)

        password = self.cleaned_data["new_password1"]
        self.user.is_active = True
        self.user.set_password(password)
        self.user.save()

        self.instance.user = self.user
        self.instance.save()

        return self.instance

    class Meta:
        model = Person
        exclude = ['user']
