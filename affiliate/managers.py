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
        link = self.cleaned_data.get('link_direct')
        if self.instance.pk and link != self.instance.link_direct:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )
        return link

    def clean_link_whatsapp(self):
        link = self.cleaned_data.get('link_whatsapp')
        if self.instance.pk and link != self.instance.link_whatsapp:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )
        return link

    def clean_link_facebook(self):
        link = self.cleaned_data.get('link_facebook')
        if self.instance.pk and link != self.instance.link_facebook:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )
        return link

    def clean_link_twitter(self):
        link = self.cleaned_data.get('link_twitter')
        if self.instance.pk and link != self.instance.link_twitter:
            raise managers.forms.ValidationError(
                'Você não pode editar este link'
            )
        return link
