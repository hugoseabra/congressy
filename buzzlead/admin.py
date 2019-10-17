from django.contrib import admin

from .models import BuzzLeadCampaign


@admin.register(BuzzLeadCampaign)
class BuzzLeadCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'campaign_id',
        'get_signature_price',
        'get_congressy_percent',
        'created_display',
        'pk',
        'active',
    )
    raw_id_fields = ['event']
    readonly_fields = ['created',
                       'modified',
                       # 'paid',
                       'signature_price']
    search_fields = [
        'event__pk',
        'campaign_id',
        'signature_email',
        'campaign_owner_token',
        'event__name',
        'event__organization__name',
    ]

    def get_signature_price(self, instance):
        return 'R$ {}'.format(round(instance.signature_price, 2))

    def get_congressy_percent(self, instance):
        return '{}%'.format(round(instance.congressy_percent, 2))

    get_signature_price.__name__ = 'R$ Assinatura'
    get_congressy_percent.__name__ = '% Congressy'
