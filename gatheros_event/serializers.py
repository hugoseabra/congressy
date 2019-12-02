from typing import Any

from kanu_locations.serializers import CitySerializer
from rest_framework import serializers

from gatheros_event.models import Person, Event, Organization, Category, Info


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

    def to_representation(self, instance: Any) -> Any:
        ret = super().to_representation(instance)

        if instance.city_id:
            city = instance.city
            ret['city_data'] = {
                'id': city.pk,
                'name': city.name,
                'uf': city.uf,
            }

        if instance.user_id:
            user = instance.user
            ret['user_data'] = {
                'id': user.pk,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login': user.last_login,
            }

        return ret


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            'pk',
            'name',
            'description',
            'description_html',
            'slug',
            'email',
            'phone',
            'website',
            'facebook',
            'twitter',
            'linkedin',
            'skype',
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)


class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Info
        fields = (
            'description',
            'description_html',
            'lead',
            'image_main',
            'youtube_video',
            'voucher_extra_info',
        )


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    organization = OrganizationSerializer()
    info = InfoSerializer()

    class Meta:
        model = Event
        fields = (
            'pk',
            'name',
            'slug',
            'published',
            'boleto_limit_days',
            'congressy_percent',
            'expected_subscriptions',
            'business_status',
            'date_start',
            'date_end',
            'created',
            'is_scientific',
            'category',
            'organization',
            'info',
        )

    def to_representation(self, instance: Event):
        ret = super().to_representation(instance)
        ret['num_subscriptions'] = instance.subscriptions.count()
        ret['num_lots'] = instance.lots.count()
        ret['num_categories'] = instance.lot_categories.count()
        ret['num_surveys'] = instance.surveys.count()

        return ret
