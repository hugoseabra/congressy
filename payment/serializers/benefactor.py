from rest_framework import serializers
from rest_framework.fields import empty

from core.serializers import FormSerializerMixin
from gatheros_event.locale import locales
from payment.managers import BenefactorManager
from payment.models import Benefactor


class BenefactorSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = BenefactorManager
        model = Benefactor
        fields = '__all__'

    def run_validation(self, data=empty):

        if data and isinstance(data, dict):
            is_br = data.get('country') == locales.BRASIL['codes']['digits_2']
            is_company = data.get('is_company', False)

            filter_search = {
                'beneficiary_id': data.get('beneficiary')
            }

            if is_company is False:
                if is_br:
                    filter_search['cpf'] = data.get('cpf')

                else:
                    filter_search['doc_type'] = data.get('doc_type')
                    filter_search['doc_number'] = \
                        data.get('doc_number').strip()
            else:
                if is_br:
                    filter_search['cnpj'] = data.get('cnpj')

                else:
                    filter_search['doc_type'] = data.get('doc_type')
                    filter_search['doc_number'] = \
                        data.get('doc_number').strip()

            try:
                self.instance = self.Meta.model.objects.get(**filter_search)
            except self.Meta.model.DoesNotExist:
                pass

        return super().run_validation(data)

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
