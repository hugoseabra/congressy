from rest_framework import serializers

from core.serializers import FormSerializerMixin
from payment.managers import BenefactorManager
from payment.models import Benefactor


class BenefactorSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = BenefactorManager
        model = Benefactor
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.city_id:
            city = instance.city

            rep['city_data'] = {
                'pk': instance.city_id,
                'name': city.name,
                'uf': city.uf,
            }

        person = instance.beneficiary
        rep['beneficiary_data'] = {
            'pk': person.pk,
            'name': person.name,
            'email': person.email,
            'user': person.user_id,
        }

        if instance.beneficiary.user_id:
            user = instance.beneficiary.user
            rep['beneficiary_data']['user_data'] = {
                'pk': user.pk,
                'fist_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login': user.last_login,
            }

        return rep
