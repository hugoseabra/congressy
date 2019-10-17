from rest_framework import serializers

from buzzlead.models import BuzzLeadCampaign


class BuzzLeadCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuzzLeadCampaign
        fields = '__all__'
