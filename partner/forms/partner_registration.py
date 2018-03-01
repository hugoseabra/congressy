from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six

from gatheros_event.forms import ProfileCreateForm
from gatheros_event.models import Organization, Member
from mailer.services import notify_new_partner, notify_new_partner_internal
from partner.models import Partner


class PartnerRegistrationForm(ProfileCreateForm):

    partner = None

    def save(self, domain_override=None, request=None,
             commit=True,
             subject_template='registration/account_confirmation_subject.txt',
             email_template='registration/account_confirmation_email.html'):
        """
        Cria uma conta no sistema

        """

        super(ProfileCreateForm, self).save(commit=True)

        # Criando usuário
        if not self.user:
            self.user = User.objects.create_user(
                username=self.cleaned_data["email"],
                email=self.cleaned_data["email"],
                password=str(uuid4())
            )

            self.user.save()

        # Vinculando usuário ao perfil
        self.instance.user = self.user
        self.instance.save()

        self.partner = Partner(person=self.instance)
        self.partner.save()

        if not self.instance.members.count():
            org = Organization(internal=False, name=self.instance.name)

            for attr, value in six.iteritems(self.instance.get_profile_data()):
                setattr(org, attr, value)

            org.save()

            Member.objects.create(
                organization=org,
                person=self.instance,
                group=Member.ADMIN
            )

        email = self.cleaned_data["email"]

        context = {
            'partner_name': self.user.get_full_name(),
            'nome': self.user.first_name,
            'partner_email': email,
            'site_name': get_current_site(request)
        }

        notify_new_partner(context)
        notify_new_partner_internal(context)

        return self.instance
