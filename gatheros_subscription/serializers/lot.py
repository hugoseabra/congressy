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

    def to_representation(self, instance: Any) -> Any:
        ret = super().to_representation(instance)

        event = instance.event
        ret['event_data'] = {
            'id': event.pk,
            'name': event.name,
            'slug': event.slug,
        }

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
