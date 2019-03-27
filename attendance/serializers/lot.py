from rest_framework import serializers

from gatheros_subscription.models import Lot

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class LotSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Lot
        fields = (
            'id',
            'name',
            'price',
            'limit',
            'private',
            'category',
            'date_start',
            'date_end',
        )
