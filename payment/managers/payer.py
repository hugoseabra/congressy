from django.forms import ValidationError, forms

from base import managers
from payment.models import Payer


class PayerManager(managers.Manager):
    """ Manager de Payers. """

    class Meta:
        model = Payer
        fields = '__all__'

    def clean_benefactor(self):
        benefactor_id = self.cleaned_data.get('benefactor')

        if self.instance.pk and self.instance.benefactor_id != benefactor_id:
            raise forms.ValidationError('Você não pode editar autor do'
                                        ' pagamento.')

        return benefactor_id

    def clean(self):
        """
            Regra de integridade: A pessoa da inscrição é a mesma beneficária
                do pagador.

            Regra de integridade: A relação entre inscrição e beneficária
                deve ser unica.

        """
        clean_data = super().clean()
        subscription = clean_data.get('subscription')
        benefactor = clean_data.get('beneficiary')

        if benefactor.beneficiary.person.id != subscription.person.id:
            raise ValidationError({
                'subscription': 'A pessoa da inscrição deve ser a  mesma '
                                'beneficária do pagador'
            })

        if Payer.objects.filter(beneficiary=benefactor,
                                subscription=subscription).exists():
            raise ValidationError({
                'beneficiary': 'Esse beneficiário já está vinculado a '
                               'essa inscrição'
            })

        return clean_data
