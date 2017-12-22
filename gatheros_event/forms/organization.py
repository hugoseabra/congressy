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
    internal = False

    class Meta:
        model = Organization
        # fields = (
        #     'name',
        #     'description_html',
        #     'avatar',
        #     'website',
        #     'facebook',
        #     'twitter',
        #     'linkedin',
        #     'skype',
        # )

        fields = (
            'name',
            'description_html',
            'website',
            'facebook',
            'twitter',
            'linkedin',
            'skype',
        )


    def __init__(self, user, internal=False, data=None, *args, **kwargs):
        self.user = user
        self.internal = internal

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
        """ Salva dados. """
        # noinspection PyProtectedMember
        is_new = self.instance._state.adding
        self.instance.internal = self.internal

        if is_new:
            self.instance.active = True

        result = super(OrganizationForm, self).save(commit=commit)
        if is_new:
            self.instance.members.create(
                person=self.user.person,
                group=Member.ADMIN
            )

        return result


class OrganizationManageMembershipForm(forms.Form):
    """ Formulário de gerenciamento de membros de organização. """
    organization = None

    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        super(OrganizationManageMembershipForm, self).__init__(*args, **kwargs)

    def deactivate(self, user):
        """ Desativa membro da organização. """
        member = self._get_member(user)
        member.active = False
        member.save()

    def activate(self, user):
        """ Ativa membro da organização. """
        member = self._get_member(user)
        member.active = True
        member.save()

    def delete(self, user):
        """ Remove membro da organização. """
        member = self._get_member(user)
        member.delete()

    def _get_member(self, user):
        try:
            return Member.objects.get(
                organization=self.organization,
                person=user.person
            )

        except Exception:
            raise Exception(
                'Não foi possível realizar cancelamento: membro `{}` não é da'
                ' organização `{}`.'.format(
                    user.get_full_name(),
                    self.organization.name
                )
            )
