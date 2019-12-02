import base64
import binascii
from typing import Any
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers

from addon import models
from addon.services import SubscriptionServiceService
from core.serializers import FormSerializerMixin
from gatheros_subscription.models import LotCategory, Subscription


class LotCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LotCategory
        fields = (
            'id',
            'name',
        )


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = '__all__'


class OptionalProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OptionalProductType
        fields = '__all__'


class OptionalServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OptionalServiceType
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        self.subscription = None
        if 'subscription' in kwargs:
            sub_pk = kwargs.pop('subscription')
            try:
                self.subscription = Subscription.objects.get(pk=sub_pk)
            except Subscription.DoesNotExist:
                raise Exception('Subscription not found.')

        data = kwargs.get('data')

        if data:
            possible_base64 = data.get('banner')
            if possible_base64:
                # Decoding from base64 avatar into a file obj.
                try:
                    file_ext, imgstr = possible_base64.split(';base64,')
                    ext = file_ext.split('/')[-1]
                    file_name = str(uuid4()) + "." + ext
                    data._mutable = True
                    data['banner'] = ContentFile(
                        base64.b64decode(imgstr),
                        name=file_name
                    )
                    data._mutable = False
                    kwargs.update({'data': data})
                except (binascii.Error, ValueError):
                    pass

        super().__init__(*args, **kwargs)

    def to_representation(self, instance: Any) -> Any:
        ret = super().to_representation(instance)

        opt_type = instance.optional_type
        ret['optional_type_data'] = {
            'id': opt_type.pk,
            'name': opt_type.name,
        }

        lot_cat = instance.lot_category
        ret['lot_category_data'] = {
            'id': lot_cat.pk,
            'name': lot_cat.name,
            'active': lot_cat.active,
            'description': lot_cat.description,
        }

        ret['num_subscriptions'] = instance.num_consumed
        ret['limit'] = instance.quantity

        ret['status'] = instance.status
        ret['full'] = False
        ret['conflicted'] = False
        ret['conflict_reason'] = None
        ret['subscription_registered'] = False

        if instance.has_quantity_conflict:
            ret['full'] = True
            ret['conflicted'] = True
            ret['conflict_reason'] = 'Esta opção está esgotada.'

        elif self.subscription:
            try:
                addon_prod = instance.subscription_products.get(
                    pk=self.subscription.pk
                )
                ret['subscription_registered'] = True
                if addon_prod.has_tag_conflict is True:
                    ret['conflicted'] = True
                    ret['conflict_reason'] = 'Já existe outra opção' \
                                             ' semelhante selecionada.'
            except ObjectDoesNotExist:
                pass

        return ret


class SubscriptionProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubscriptionProduct
        fields = ('pk', 'subscription', 'optional',)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        self.subscription = None
        if 'subscription' in kwargs:
            sub_pk = kwargs.pop('subscription')
            try:
                self.subscription = Subscription.objects.get(pk=sub_pk)
            except Subscription.DoesNotExist:
                raise Exception('Subscription not found.')

        data = kwargs.get('data')

        if data:
            possible_base64 = data.get('banner')
            if possible_base64:
                # Decoding from base64 avatar into a file obj.
                try:
                    file_ext, imgstr = possible_base64.split(';base64,')
                    ext = file_ext.split('/')[-1]
                    file_name = str(uuid4()) + "." + ext
                    data._mutable = True
                    data['banner'] = ContentFile(
                        base64.b64decode(imgstr),
                        name=file_name
                    )
                    data._mutable = False
                    kwargs.update({'data': data})
                except (binascii.Error, ValueError):
                    pass

        super().__init__(*args, **kwargs)

    def to_representation(self, instance: models.Service) -> Any:
        ret = super().to_representation(instance)

        theme = instance.theme
        ret['theme_data'] = {
            'id': theme.pk,
            'name': theme.name,
            'limit': theme.limit,
        }

        ret['price'] = instance.price

        ret['num_subscriptions'] = instance.num_consumed
        ret['limit'] = instance.quantity

        ret['status'] = instance.status
        ret['full'] = False
        ret['conflicted'] = False
        ret['conflict_reason'] = None
        ret['subscription_registered'] = False

        if instance.has_quantity_conflict:
            ret['full'] = True
            ret['conflicted'] = True
            ret['conflict_reason'] = 'Esta opção está esgotada.'

        elif self.subscription:
            try:
                addon_serv = instance.subscription_services.get(
                    subscription_id=self.subscription.pk
                )
                ret['subscription_registered'] = True

                if addon_serv.has_tag_conflict is True:
                    ret['conflicted'] = True
                    ret['conflict_reason'] = 'Já existe outra opção' \
                                             ' semelhante selecionada.'
                elif addon_serv.has_schedule_conflicts is True:
                    ret['conflicted'] = True
                    ret['conflict_reason'] = 'Opção em conflito de horário' \
                                             ' com outra opção previamente' \
                                             ' selecionada.'
                elif addon_serv.has_theme_conflict is True:
                    ret['conflicted'] = True
                    ret['conflict_reason'] = 'Opção possui um tema que' \
                                             ' está esgotado ou indisponível.'
            except ObjectDoesNotExist:
                pass

        opt_type = instance.optional_type
        ret['optional_type_data'] = {
            'id': opt_type.pk,
            'name': opt_type.name,
        }

        lot_cat = instance.lot_category
        ret['lot_category_data'] = {
            'id': lot_cat.pk,
            'name': lot_cat.name,
            'active': lot_cat.active,
            'description': lot_cat.description,
        }

        return ret


class SubscriptionServiceSerializer(FormSerializerMixin,
                                    serializers.ModelSerializer):
    class Meta:
        form = SubscriptionServiceService
        model = models.SubscriptionService
        fields = ('pk', 'subscription', 'optional',)
