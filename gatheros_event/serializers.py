from kanu_locations.serializers import CitySerializer
from rest_framework import serializers

from gatheros_event.models import Person, Event, Organization, Category, Info


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


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
