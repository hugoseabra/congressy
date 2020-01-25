from typing import Any

import absoluteuri
from rest_framework import serializers

from gatheros_event.helpers.event_business import is_free_event
from gatheros_event.helpers.event_subscribable import (
    is_event_subscribable,
    has_enabled_private_lots,
)
from gatheros_event.models import (
    Category,
    Event,
    Info,
    Organization,
    Person,
    Place,
)


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
            'show_banner',
            'image_main',
            'image_main2',
            'youtube_video',
            'voucher_extra_info',
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        main_default = None
        main_thumbnail = None

        if instance.image_main:
            main_default = absoluteuri.build_absolute_uri(
                instance.image_main.default.url
            )
            main_thumbnail = absoluteuri.build_absolute_uri(
                instance.image_main.thumbnail.url
            )

        main2_default = None
        main2_thumbnail = None

        if instance.image_main2:
            main2_default = absoluteuri.build_absolute_uri(
                instance.image_main2.default.url
            )
            main2_thumbnail = absoluteuri.build_absolute_uri(
                instance.image_main2.thumbnail.url
            )

        rep['banners'] = {
            'image_main': {
                'default': main_default if main_default else None,
                'thumbnail': main_thumbnail if main_thumbnail else None,
            },
            'image_main2': {
                'default': main2_default if main2_default else None,
                'thumbnail': main2_thumbnail if main2_thumbnail else None,
            }
        }

        return rep


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = (
            'name',
            'country',
            'city',
            'city_international',
            'state_international',
            'zoom',
            'lat',
            'long',
            'reference',
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if rep['city']:
            rep['city_name'] = instance.city.name
            rep['state'] = instance.city.uf

        return rep


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    organization = OrganizationSerializer()
    info = InfoSerializer()
    place = PlaceSerializer()

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
            'hotsite_version',
            'info',
            'place',
        )

    def to_representation(self, instance: Event):
        ret = super().to_representation(instance)
        ret['num_subscriptions'] = instance.subscriptions.count()
        ret['num_lots'] = instance.lots.count()
        ret['num_categories'] = instance.lot_categories.count()
        ret['num_surveys'] = instance.surveys.count()

        ret['free'] = is_free_event(instance) is True
        ret['subscriptions_enabled'] = is_event_subscribable(instance) is True
        ret['has_enabled_private_lots'] = \
            has_enabled_private_lots(instance) is True

        prices = list()
        for lot in instance.lots.filter(private=False, active=True):
            if lot.running is False:
                continue

            if lot.price:
                prices.append(lot.get_calculated_price())
            else:
                prices.append(0)

        ret['min_price'] = round(min(prices), 2) if prices else '0.00'
        ret['max_price'] = round(max(prices), 2) if prices else '0.00'

        return ret
