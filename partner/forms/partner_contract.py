"""
    Partner Contract Form used to validate domain and business rules
"""
from django import forms
from django.db.models import Sum
from django.conf import settings

from partner.models import PartnerContract


class PartnerContractForm(forms.ModelForm):
    """ Partner Contract Form  Implementation"""

    class Meta:
        model = PartnerContract
        fields = '__all__'

    def _post_clean(self):
        super()._post_clean()
        event = self.cleaned_data.get('event')

        if not event:
            return

        partner_plan = self.cleaned_data.get('partner_plan')
        partner_max_percentage = settings.PARTNER_MAX_PERCENTAGE_IN_EVENT
        total_query = event.partner_contracts.aggregate(Sum(
            'partner_plan__percent'))

        total = total_query.get('partner_plan__percent__sum')

        if partner_plan.percent > partner_max_percentage:
            percent_to_high = 'O valor da porcentagem do plano ultrapassa {}%'.\
                format(partner_max_percentage)
            self.add_error('__all__', percent_to_high)
        elif total and (total + partner_plan.percent) > partner_max_percentage:

            to_high_validation_error = 'A soma de todos os parceiros do ' \
                                       'evento  não deve ultrapassar a {}%' \
                                       ' do rateamento do montante da' \
                                       ' Congressy. Porcentagem total até o' \
                                       ' momento {}%'. format(
                                            partner_max_percentage,
                                            total
                                        )

            self.add_error('__all__', to_high_validation_error)


