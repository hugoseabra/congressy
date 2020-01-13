from collections import OrderedDict

from rest_framework import serializers

from core.serializers import FormSerializerMixin
from .forms import AccountCreateForm


class AccountSerializer(FormSerializerMixin, serializers.Serializer):
    class Meta:
        form = AccountCreateForm

    def save(self, request, **_):
        assert self.form_instance is not None
        self.instance = self.form_instance.create(request=request)
        return self.instance

    def to_internal_value(self, data):
        return data

    def to_representation(self, instance):

        avatar_url = None
        if instance.avatar.name:
            avatar_url = instance.avantar.url

        ret = OrderedDict({
            "uuid": instance.pk,
            "name": instance.name,
            "gender": instance.gender,
            "email": instance.email,
            "city_international": instance.city_international,
            "zip_code": instance.zip_code,
            "zip_code_international": instance.zip_code_international,
            "street": instance.street,
            "number": instance.number,
            "complement": instance.complement,
            "village": instance.village,
            "state_international": instance.state_international,
            "address_international": instance.address_international,
            "country": instance.country,
            "ddi": instance.ddi,
            "phone": instance.phone,
            "avatar": avatar_url,
            "cpf": instance.cpf,
            "international_doc_type": instance.international_doc_type,
            "international_doc": instance.international_doc,
            "birth_date": instance.birth_date,
            "rg": instance.rg,
            "orgao_expedidor": instance.orgao_expedidor,
            "created": instance.created,
            "modified": instance.modified,
            "synchronized": instance.synchronized,
            "term_version": instance.term_version,
            "politics_version": instance.politics_version,
            "pne": instance.pne,
            "institution": instance.institution,
            "institution_cnpj": instance.institution_cnpj,
            "function": instance.function,
            "website": instance.website,
            "facebook": instance.facebook,
            "twitter": instance.twitter,
            "linkedin": instance.linkedin,
            "skype": instance.skype,
            "city": instance.city_id,
            "user": instance.user_id,
            "occupation": instance.occupation,
        })

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
