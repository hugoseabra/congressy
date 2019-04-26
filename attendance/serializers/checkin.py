from rest_framework import serializers

from attendance import models

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checkin
        fields = '__all__'

    def validate_subscription(self, value):
        if value.confirmed is False:
            raise serializers.ValidationError(
                'Esta inscrição não está confirmada.'
            )

        return value

    def validate(self, attrs):
        subscription = attrs.get('subscription')
        service = attrs.get('attendance_service')
        checkins = subscription.checkins.filter(
            attendance_service_id=service.pk,
            checkout__isnull=True,
        )

        if checkins.count():
            raise serializers.ValidationError({
                'subscription': 'Entrada já registrada neste Atendimento para'
                                ' esta inscrição.'
            })

        return attrs
