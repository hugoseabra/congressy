from kanu_locations.serializers import CitySerializer
from rest_framework import serializers

from gatheros_event.models import Person, Event, Organization, Category


class PersonSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Person
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            'name',
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


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    organization = OrganizationSerializer()

    class Meta:
        model = Event
        fields = (
            'name',
            'slug',
            'date_start',
            'date_end',
            'created',
            'is_scientific',
            'category',
            'organization',
        )
