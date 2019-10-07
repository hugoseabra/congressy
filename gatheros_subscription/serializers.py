from typing import Any

import absoluteuri
from django.urls import reverse
from rest_framework import serializers

from gatheros_event.models import Person, Event
from gatheros_subscription.models import Subscription, Lot
from kanu_locations.models import City


class SerializerDinamicField(serializers.Field):
    def __init__(self, dinamic_field=None, **kwargs):
        self.dinamic_field = dinamic_field
        kwargs['source'] = '*'
        kwargs['label'] = dinamic_field.label
        super(SerializerDinamicField, self).__init__(**kwargs)

    def to_representation(self, instance):
        # try:
        #     answer = instance.answers.get(field=self.dinamic_field)
        #     return answer.value.get('output')
        #
        # except Answer.DoesNotExist:
        return None

    def to_internal_value(self, data):
        pass


class CityExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = (
            'name',
            'uf',
        )


class PersonExportSerializer(serializers.ModelSerializer):
    city = CityExportSerializer()

    class Meta:
        model = Person
        fields = (
            'name',
            'gender',
            'city',
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id',
            'name',
            'date_start',
            'date_end',
        )


class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = '__all__'

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


class SubscriptionExportSerializer(serializers.ModelSerializer):
    person = PersonExportSerializer()
    lot = serializers.CharField(source='lot.name')

    @staticmethod
    def setup_prefetch(queryset):
        """
        Configura o pré carregamento de dados para melhorar performace

        :param queryset:
        :return: queryset
        """

        # Prefetch das respostas
        # queryset = queryset.prefetch_related('answers')
        return queryset

    class Meta:
        model = Subscription
        fields = [
            'count',
            'lot',
            'code',
            'person',
        ]


class CheckInPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            'name',
            'email',
            'cpf',
            'institution_cnpj',
        )


class CheckInSubscriptionSerializer(serializers.ModelSerializer):
    person = CheckInPersonSerializer()
    lot = serializers.CharField(source='lot.name')

    class Meta:
        model = Subscription
        fields = [
            'pk',
            'code',
            'person',
            'lot',
            'status',
            'event_count',
        ]


class SubscriptionSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        rep = {
            'pk': obj.pk,
            'person_pk': obj.person.pk,
            'person_name': obj.person.name,
            'person_email': obj.person.email,
            'person_cpf': obj.person.cpf,
            'person_city': None,
            'person_uf': None,
            'person_phone': obj.person.phone,
            'person_city_international': obj.person.city_international,
            'person_international_doc': obj.person.international_doc,
            'origin': obj.origin,
            'code': obj.code,
            'accredited': obj.accredited,
            'accredited_on': obj.accredited_on,
            'lot_name': obj.lot.name,
            'event_count': obj.event_count,
            'test_subscription': obj.test_subscription,
            'status': obj.status,
            'created': obj.created,
            'tag_info': obj.tag_info,
            'tag_group': obj.tag_group,
            'category_name': None,
            'institution': None,
            'link': absoluteuri.reverse(
                'subscription:subscription-view', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            ),
            'edit_link': None,
            'voucher_link': None,
            'debts_amount': obj.debts_amount,
        }

        if obj.confirmed:
            rep['voucher_link'] = absoluteuri.reverse(
                'subscription:subscription-voucher', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            ),

        if obj.event.allow_internal_subscription:
            rep['edit_link'] = absoluteuri.reverse(
                'subscription:subscription-edit', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            )

        if obj.lot.category:
            rep['category_name'] = obj.lot.category.name

        if obj.person.city:
            rep['person_city'] = obj.person.city.name
            rep['person_uf'] = obj.person.city.uf

        if obj.person.institution:
            rep['institution'] = obj.person.institution

        return rep


class SubscriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'pk',
            'person',
            'lot',
            'completed',
            'test_subscription',
            'accredited',
            'accredited_on',
            'created_by',
            'origin',
        ]

    def to_representation(self, obj):
        rep = {
            'pk': obj.pk,
            'name': obj.person.name,
            'email': obj.person.email,
            'person': obj.person_id,
            'origin': obj.origin,
            'code': obj.code,
            'event': obj.event_id,
            'event_slug': obj.event.slug,
            'category': None,
            'category_name': None,
            'lot': obj.lot_id,
            'lot_name': obj.lot.name,
            'accredited': obj.accredited,
            'accredited_on': obj.accredited_on,
            'event_count': obj.event_count,
            'completed': obj.test_subscription,
            'notified': obj.test_subscription,
            'test_subscription': obj.test_subscription,
            'status': obj.status,
            'created': obj.created,
            'tag_info': obj.tag_info,
            'tag_group': obj.tag_group,
            'voucher_link': None,
            'debts_amount': obj.debts_amount,
        }

        if obj.confirmed:
            rep['voucher_link'] = absoluteuri.build_absolute_uri(reverse(
                'subscription:subscription-voucher', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                })),

        if obj.lot.category_id:
            rep['category'] = obj.lot.category_id
            rep['category_name'] = obj.lot.category.name

        return rep
