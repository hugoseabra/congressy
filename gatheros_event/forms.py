from django.shortcuts import reverse
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from core.fields import MultiEmailField
from .models import Invitation, Organization
from .models.rules import check_invite


class InvitationForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        empty_label='-----',
        label='Organização'
    )
    to = MultiEmailField(label='Emails')
    user = None
    _invites = None

    def __init__(self, user, data=None, *args, **kwargs):
        super(InvitationForm, self).__init__(data=data, *args, **kwargs)

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
                type=Invitation.INVITATION_TYPE_HELPER
            )

            # Submete os convites as regras
            check_invite(invite)

            # Adiciona na lista dos convites que estão ok
            self._invites.append(invite)

    def send_invite(self):
        for invite in self._invites:
            url = reverse(
                'gatheros_event:organization-invite-accept',
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
