"""
Formulários de Organization
"""

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from gatheros_event.models import Member, Organization


class OrganizationForm(forms.ModelForm):
    """Formulário principal de evento"""

    user = None

    class Meta:
        model = Organization
        fields = (
            'name',
            'description_html',
            'avatar',
            'website',
            'facebook',
            'twitter',
            'linkedin',
            'skype',
        )

    def __init__(self, user, data=None, *args, **kwargs):
        self.user = user

        try:
            self.user.person
        except ObjectDoesNotExist:
            raise IntegrityError(
                'Usuário não possui vínculo com pessoa, portanto, não é pode'
                ' ser um membro.'
            )

        instance = kwargs.get('instance')
        if instance and not instance.is_member(user):
            raise ValidationError({
                '__all__': 'Usuário não possui qualquer vínculo com a'
                           ' organização.'
            })

        super(OrganizationForm, self).__init__(data=data, *args, **kwargs)

    def save(self, commit=True):
        is_new = self.instance._state.adding
        self.instance.internal = False
        self.instance.active = True

        result = super(OrganizationForm, self).save(commit=commit)
        if is_new:
            self.instance.members.create(
                person=self.user.person,
                group=Member.ADMIN
            )

        return result
