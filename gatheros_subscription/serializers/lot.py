from typing import Any

from rest_framework import serializers

from gatheros_subscription.models import Lot, LotCategory


class LotCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LotCategory
        fields = '__all__'


class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = '__all__'

    def to_representation(self, instance: Lot) -> Dict:
        ret = super().to_representation(instance)

        event = instance.event
        ret['event_data'] = {
            'id': event.pk,
            'name': event.name,
            'slug': event.slug,
        }

        if instance.private is False:
            ret['exhibition_code'] = None

        ret['status'] = instance.status
        ret['num_subscriptions'] = instance.subscriptions.count()

        lot_cat = instance.category
        ret['category_data'] = {
            'id': lot_cat.pk,
            'name': lot_cat.name,
            'active': lot_cat.active,
        }

        if instance.event_survey_id:
            survey = instance.event_survey
            ret['event_survey_data'] = {
                'id': survey.pk,
                'name': survey.survey.name,
                'description': survey.survey.description,
            }

        ret['price'] = instance.get_calculated_price()
        ret['liquid_price'] = instance.get_liquid_price()

        return ret

    def validate_exhibition_code(self, value):
        if value:
            event = self.instance.event.pk
            existing = Lot.objects.filter(
                event_id=event,
                exhibition_code=value.upper(),
            ).exclude(pk=self.instance.pk)

            if existing.count() > 0:
                msg = "Cupom com esse código já existe no evento!"
                raise serializers.ValidationError(msg)

        return value.upper() if value else None
