from django.urls import reverse
from kanu_locations.models import City
from rest_framework import serializers

from gatheros_event.models import Person, Event
from gatheros_subscription.models import Subscription, Lot


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
    event = EventSerializer()

    class Meta:
        model = Lot
        fields = '__all__'

    def validate_exhibition_code(self, value):
        event = self.instance.event.pk
        existing = Lot.objects.filter(
            event_id=event,
            exhibition_code=value.upper(),
        ).exclude(pk=self.instance.pk)

        if existing.count() > 0:
            msg = "Cupom com esse código já existe no evento!"
            raise serializers.ValidationError(msg)

        return value.upper()


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
            'person.name': obj.person.name,
            'person.email': obj.person.email,
            'person.cpf': obj.person.cpf,
            'person.city': obj.person.city.name,
            'person.uf': obj.person.city.uf,
            'person.phone': obj.person.phone,
            'person.city_international': obj.person.city_international,
            'person.international_doc': obj.person.international_doc,
            'origin': obj.origin,
            'code': obj.code,
            'lot.name': obj.lot.name,
            'event_count': obj.event_count,
            'test_subscription': obj.test_subscription,
            'status': obj.status,
            'created': obj.created,
            'category.name': None,
            'link': reverse(
                'subscription:subscription-view', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            ),
            'edit_link': None,
            'voucher_link': None,
        }

        if obj.confirmed:
            rep['voucher_link'] = reverse(
                'subscription:subscription-voucher', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }),

        if obj.event.allow_internal_subscription:
            rep['edit_link'] = reverse(
                'subscription:subscription-edit', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }),

        if obj.lot.category:
            rep['category.name'] = obj.lot.category.name

        return rep

    class Meta:

        datatables_always_serialize = (
            'person.name',
            'person.cpf',
            'person.city',
            'person.uf',
            'person.phone',
            'person.city_international',
            'person.international_doc',
            'origin',
            'code',
            'lot.name',
            'event_count',
            'test_subscription',
            'status',
            'created',
            'category.name',
            'link',
            'edit_link',
            'voucher_link',
        )
