import json

from rest_framework import serializers

from gatheros_event.models import Person
from gatheros_subscription.models import Subscription


class SerializerDinamicField(serializers.Field):
    def __init__(self, dinamic_field=None, **kwargs):
        self.dinamic_field = dinamic_field
        kwargs['source'] = '*'
        kwargs['label'] = dinamic_field.label
        super(SerializerDinamicField, self).__init__(**kwargs)

    def to_representation(self, instance):
        value = instance.answers.get(field=self.dinamic_field).value
        return json.loads(value)['output']


class PersonExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            'uuid',
            'name',
            'gender',
            'city',
        )


class SubscriptionExportSerializer(serializers.ModelSerializer):
    person = PersonExportSerializer()
    lot = serializers.CharField(source='lot.name')

    def __init__(self, *args, **kwargs):
        """ Inicialização do objeto """
        super(SubscriptionExportSerializer, self).__init__(*args, **kwargs)

        # Adicionando os campos dinâmicos
        queryset = kwargs.get('data')
        instance = queryset.first()
        fields = instance.event.form.fields.filter(form_default_field=False)
        for field in fields:
            self.fields[field.name] = SerializerDinamicField(field)

    @staticmethod
    def setup_prefetch(queryset):
        """
        Configura o pré carregamento de dados para melhorar performace

        :param queryset:
        :return: queryset
        """

        # Prefetch das respostas
        queryset = queryset.prefetch_related('answers')
        return queryset

    class Meta:
        model = Subscription
        fields = [
            'count',
            'synchronized',
            'origin',
            'lot',
            'code',
            'person',
        ]
