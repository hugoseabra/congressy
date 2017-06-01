# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""

from django import forms

from gatheros_event.models import Person


class ProfileForm(forms.ModelForm):
    """
    Pessoas que são usuários do sistema
    """

    def __init__(self, user, instance=None, data=None, *args, **kwargs):
        super(ProfileForm, self).__init__(
            instance=instance,
            data=data,
            *args,
            **kwargs
        )
        self.user = user

    def save(self, commit=True):
        super(ProfileForm, self).save(commit=commit)
        self.instance.user = self.user

        if commit:
            self.instance.save()

        return self.instance

    class Meta:
        model = Person
        exclude = ['user']
