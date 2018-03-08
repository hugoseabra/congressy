"""
    Partner Contract Form used to validate domain and business rules
"""
from django import forms
from django.conf import settings
from django.db.models import Sum

from mailer.services import notify_partner_contract
from partner.models import PartnerContract


class PartnerContractForm(forms.ModelForm):
    """ Partner Contract Form  Implementation"""

    class Meta:
        model = PartnerContract
        fields = '__all__'

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            if not self.instance.pk:
                PartnerContract.objects.get(
                    event=cleaned_data['event'],
                    partner=cleaned_data['partner']
                )

                raise forms.ValidationError(
                    'Parceiro já está vinculado a este '
                    'evento'
                )

        except PartnerContract.DoesNotExist:
            pass

        return cleaned_data

    def _post_clean(self):
        super()._post_clean()
        event = self.cleaned_data.get('event')

        if not event:  # pragma: no cover
            return

        partner_plan = self.cleaned_data.get('partner_plan')
        partner_max_percentage = settings.PARTNER_MAX_PERCENTAGE_IN_EVENT
        total_query = event.partner_contracts

        if self.instance:
            total_query = total_query.exclude(pk=self.instance.pk)

        total_query = total_query.aggregate(
            Sum('partner_plan__percent')
        )

        total = total_query.get('partner_plan__percent__sum')

        if partner_plan.percent > partner_max_percentage:
            percent_to_high = 'O valor da porcentagem do plano ultrapassa {}%'. \
                format(partner_max_percentage)
            self.add_error('__all__', percent_to_high)
        elif total and (total + partner_plan.percent) > partner_max_percentage:

            to_high_validation_error = \
                'A soma de todos os parceiros do' \
                ' evento  não deve ultrapassar a {}%' \
                ' do rateamento do montante da' \
                ' Congressy. Porcentagem total até o' \
                ' momento {}%.'.format(partner_max_percentage, total)

            self.add_error('__all__', to_high_validation_error)

    def save(self, commit=True):
        saved_instance = super().save(commit)

        context = {
            'event': self.instance.event.name,
            'organizer': self.instance.event.organization.name,
            'partner_name': self.instance.partner.person.user.first_name,
            'partner_email': self.instance.partner.person.email,

        }

        notify_partner_contract(context=context)

        return saved_instance
