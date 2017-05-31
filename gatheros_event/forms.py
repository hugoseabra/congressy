from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import reverse

from core.fields import MultiEmailField
from .models import Invitation, Member, Organization, Person
from .models.rules import check_invite


class InvitationCreateForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        empty_label='-----',
        label='Organização'
    )
    to = MultiEmailField(label='Emails')
    user = None
    _invites = None

    def __init__(self, user, data=None, *args, **kwargs):
        super(InvitationCreateForm, self).__init__(data=data, *args, **kwargs)

        organizations = Organization.objects.filter(
            members__person__user=user
        )

        orgs_can_invite = organizations

        for org in organizations:
            if not user.has_perm('gatheros_event.can_invite', org):
                orgs_can_invite = orgs_can_invite.exclude(pk=org.pk)

        self.fields['organization'].queryset = orgs_can_invite
        self.user = user
        self._invites = []

    def clean(self):
        if self.errors:
            return []

        organization = self.cleaned_data['organization']

        # Cria os convites
        for email in self.cleaned_data['to']:
            invited_user, _ = User.objects.get_or_create(
                username=email,
                defaults={'email': email}
            )
            invite = Invitation(
                author=organization.get_members(person=self.user)[0],
                to=invited_user,
                group=Member.HELPER
            )

            # Submete os convites as regras
            check_invite(invite)

            # Adiciona na lista dos convites que estão ok
            self._invites.append(invite)

    def send_invite(self):
        for invite in self._invites:
            url = reverse(
                'gatheros_event:invitation-decision',
                kwargs={'pk': str(invite.pk)}
            )
            invite.to.save()
            invite.save()
            send_mail(
                'Novo convite para organização',
                'Para aceitar clique no link: {0}'.format(url),
                settings.DEFAULT_FROM_EMAIL,
                [invite.to.email]
            )


class InvitationDecisionForm(forms.ModelForm):
    """
    Decide o resultado de um convite e suas implicações
    """

    def accept(self):
        """
        Aceita o convite e criar o membro

        :return:
        """
        user = self.instance.to

        # Se não tiver um perfil de pessoa vinculado não permite aceitar
        if not hasattr(user, 'person'):
            raise ValidationError('Usuário não tem perfil de pessoa')

        # Cria membro
        Member.objects.create(
            organization=self.instance.author.organization,
            person=user.person,
            group=self.instance.group
        )

        # Remove o convite que não é mais necessário
        self.instance.delete()

    def decline(self):
        """
        Recusa o convite
        :return:
        """
        self.instance.delete()

    class Meta:
        model = Invitation
        exclude = []


class ProfileForm(forms.ModelForm):
    """
    Pessoas que são usuários do sistema
    """

    class Meta:
        model = Person
        exclude = []
