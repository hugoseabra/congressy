from affiliate.models import Affiliate, Affiliation
from base import managers


class AffiliateManager(managers.Manager):
    """ Manager de afiliado. """

    class Meta:
        model = Affiliate
        fields = '__all__'


class AffiliationManager(managers.Manager):
    """ Manager de afiliação. """

    class Meta:
        model = Affiliation
        fields = '__all__'

    def clean_link_direct(self):
        if self.instance.pk:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )

    def clean_link_whatsapp(self):
        if self.instance.pk:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )

    def clean_link_facebook(self):
        if self.instance.pk:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )

    def clean_link_twitter(self):
        if self.instance.pk:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )
