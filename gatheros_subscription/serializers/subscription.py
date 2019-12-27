from decimal import Decimal
from typing import Any

import absoluteuri
from django.db.models import Model
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import serializers

from gatheros_subscription.models import Subscription


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
            'lot_pk': obj.lot_id,
            'lot_name': obj.lot.name,
            'lot_price': obj.lot.get_calculated_price(),
            'lot_date_start': obj.lot.date_start.strftime('%Y-%m-%d %H:%M:%S'),
            'lot_date_end': obj.lot.date_end.strftime('%Y-%m-%d %H:%M:%S'),
            'lot_status': obj.lot.status,
            'lot_status_name': obj.lot.get_status_display(),
            'event_count': obj.event_count,
            'completed': obj.completed,
            'test_subscription': obj.test_subscription,
            'status': obj.status,
            'free': obj.free,
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

        rep['created'] = obj.created.strftime('%Y-%m-%d %H:%M:%S')
        rep['modified'] = obj.modified.strftime('%Y-%m-%d %H:%M:%S')

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
            'created',
            'modified',
            'created_by',
            'origin',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['free'] = instance.free

        person = instance.person
        rep['person_data'] = {
            'pk': person.pk,
            'name': person.name,
            'email': person.email,
            'user': person.user_id,
        }

        if instance.person.user_id:
            user = instance.person.user
            rep['person_data']['user_data'] = {
                'pk': user.pk,
                'fist_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login': user.last_login,
            }

        lot = instance.lot
        amounts = list()

        amounts.append(lot.get_calculated_price())

        survey = None
        survey_data = dict()

        if lot.event_survey_id:
            survey = lot.event_survey.survey
            survey_data = {
                'pk': survey.pk,
                'name': survey.name,
                'description': survey.description,
            }

        rep['lot_data'] = {
            'pk': lot.pk,
            'name': lot.name,
            'event': lot.event_id,
            'event_data': {
                'pk': lot.event_id,
                'name': lot.event.name,
                'slug': lot.event.slug,
            },
            'price': lot.get_calculated_price(),
            'survey': survey.pk if survey else None,
            'survey_data': survey_data,
            'status': lot.status,
            'status_name': lot.get_status_display(),
        }

        if lot.category_id:
            lot_cat = lot.category
            rep['lot_data'].update({
                'category': lot.category_id,
                'category_data': {
                    'id': lot_cat.pk,
                    'name': lot_cat.name,
                    'active': lot_cat.active,
                    'description': lot_cat.description,
                }
            })

        rep['addon_products'] = list()
        addon_products = instance.subscription_products.all()

        if addon_products.count():
            for addon_sub in addon_products:
                optional = addon_sub.optional
                data = {
                    'pk': addon_sub.pk,
                    'product_id': addon_sub.optional_id,
                    'product_data': {
                        'pk': optional.pk,
                        'name': optional.name,
                        'published': optional.published,
                        'date_end_sub': optional.date_end_sub.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'banner':
                            optional.banner.url if optional.banner else None,
                        'category': {
                            'pk': optional.lot_category_id,
                            'name': optional.lot_category.name,
                            'description': optional.lot_category.description,
                        },
                        "optional_type": {
                            "name": optional.optional_type.name,
                            "pk": optional.optional_type_id,
                        },
                        'price': optional.price,
                        'banners': {
                            'default': None,
                            'thumbnail': None,
                        }
                    }
                }
                if optional.banner.name:
                    def_banner = absoluteuri.build_absolute_uri(
                        optional.banner.default.url
                    )
                    def_thumbnail = absoluteuri.build_absolute_uri(
                        optional.banner.thumbnail.url
                    )
                    data['product_data']['banners'] = {
                        'default': def_banner,
                        'thumbnail': def_thumbnail,
                    }

                rep['addon_products'].append(data)

                amounts.append(optional.price)

        rep['addon_services'] = list()
        addon_services = instance.subscription_services.all()

        if addon_services.count():
            for addon_sub in addon_services:
                optional = addon_sub.optional
                data = {
                    'pk': addon_sub.pk,
                    'service_id': addon_sub.optional_id,
                    'service_data': {
                        'pk': optional.pk,
                        'name': optional.name,
                        'date_start': optional.schedule_start.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'date_end': optional.schedule_end.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'date_end_sub': optional.date_end_sub.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'published': optional.published,
                        'banner':
                            optional.banner.url if optional.banner else None,
                        'category': {
                            'pk': optional.lot_category_id,
                            'name': optional.lot_category.name,
                            'description': optional.lot_category.description,
                        },
                        "optional_type": {
                            "name": optional.optional_type.name,
                            "pk": optional.optional_type_id,
                        },
                        'price': optional.price,
                        'banners': {
                            'default': None,
                            'thumbnail': None,
                        }
                    }
                }

                if optional.banner.name:
                    def_banner = absoluteuri.build_absolute_uri(
                        optional.banner.default.url
                    )
                    def_thumbnail = absoluteuri.build_absolute_uri(
                        optional.banner.thumbnail.url
                    )
                    data['service_data']['banners'] = {
                        'default': def_banner,
                        'thumbnail': def_thumbnail,
                    }

                rep['addon_services'].append(data)

                amounts.append(optional.price)

        paid_amount = Decimal(0)
        for trans in instance.transactions.filter(status='paid'):
            paid_amount += trans.amount

        total_amount = round(Decimal(sum(amounts)), 2)
        paid_amount = round(paid_amount, 2)

        if instance.confirmed is True:
            rep['voucher_link'] = absoluteuri.build_absolute_uri(reverse(
                'subscription:subscription-voucher',
                kwargs={
                    'event_pk': instance.event_id,
                    'pk': instance.pk,
                }
            ))

        rep['total_amount'] = total_amount
        rep['paid_amount'] = paid_amount

        return rep

    def create(self, validated_data: Any) -> Any:
        instance = super().create(validated_data)

        if instance.free is True:
            instance.status = Subscription.CONFIRMED_STATUS
            instance.save()

        return instance

    def update(self, instance: Model, validated_data: Any) -> Any:
        instance = super().update(instance, validated_data)

        if instance.free is True:
            instance.status = Subscription.CONFIRMED_STATUS
            instance.save()

        return instance


class SubscriptionBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'lot',
        ]

    def to_representation(self, instance):
        rep = dict()

        person = instance.person

        rep['person_data'] = {
            'pk': person.pk,
            'name': person.name,
            'email': person.email,
            'user': person.user_id,
        }

        if instance.person.user_id:
            user = instance.person.user
            rep['person_data']['user_data'] = {
                'pk': user.pk,
                'fist_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login': user.last_login,
            }

        lot = instance.lot
        amounts = list()

        amounts.append(lot.get_calculated_price())

        survey = None
        survey_data = dict()

        if lot.event_survey_id:
            survey = lot.event_survey.survey
            survey_data = {
                'pk': survey.pk,
                'name': survey.name,
                'description': survey.description,
            }

        rep['lot_data'] = {
            'pk': lot.pk,
            'name': lot.name,
            'event': lot.event_id,
            'event_data': {
                'pk': lot.event_id,
                'name': lot.event.name,
                'slug': lot.event.slug,
            },
            'price': lot.get_calculated_price(),
            'survey': survey.pk if survey else None,
            'survey_data': survey_data,
            'status': lot.status,
            'status_name': lot.get_status_display(),
        }

        if lot.category_id:
            lot_cat = lot.category
            rep['lot_data'].update({
                'category': lot.category_id,
                'category_data': {
                    'id': lot_cat.pk,
                    'name': lot_cat.name,
                    'active': lot_cat.active,
                    'description': lot_cat.description,
                }
            })

        rep['addon_products'] = list()
        addon_products = instance.subscription_products.all()

        if addon_products.count():
            for addon_sub in addon_products:
                optional = addon_sub.optional
                data = {
                    'pk': addon_sub.pk,
                    'product_id': addon_sub.optional_id,
                    'product_data': {
                        'pk': optional.pk,
                        'name': optional.name,
                        'published': optional.published,
                        'date_end_sub': optional.date_end_sub.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'banner':
                            optional.banner.url if optional.banner else None,
                        'category': {
                            'pk': optional.lot_category_id,
                            'name': optional.lot_category.name,
                            'description': optional.lot_category.description,
                        },
                        "optional_type": {
                            "name": optional.optional_type.name,
                            "pk": optional.optional_type_id,
                        },
                        'price': optional.price,
                        'banners': {
                            'default': None,
                            'thumbnail': None,
                        }
                    }
                }
                if optional.banner.name:
                    def_banner = absoluteuri.build_absolute_uri(
                        optional.banner.default.url
                    )
                    def_thumbnail = absoluteuri.build_absolute_uri(
                        optional.banner.thumbnail.url
                    )
                    data['product_data']['banners'] = {
                        'default': def_banner,
                        'thumbnail': def_thumbnail,
                    }

                rep['addon_products'].append(data)

                amounts.append(optional.price)

        rep['addon_services'] = list()
        addon_services = instance.subscription_services.all()

        if addon_services.count():
            for addon_sub in addon_services:
                optional = addon_sub.optional
                data = {
                    'pk': addon_sub.pk,
                    'service_id': addon_sub.optional_id,
                    'service_data': {
                        'pk': optional.pk,
                        'name': optional.name,
                        'date_start': optional.schedule_start.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'date_end': optional.schedule_end.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'date_end_sub': optional.date_end_sub.strftime(
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'published': optional.published,
                        'banner':
                            optional.banner.url if optional.banner else None,
                        'category': {
                            'pk': optional.lot_category_id,
                            'name': optional.lot_category.name,
                            'description': optional.lot_category.description,
                        },
                        "optional_type": {
                            "name": optional.optional_type.name,
                            "pk": optional.optional_type_id,
                        },
                        'price': optional.price,
                        'banners': {
                            'default': None,
                            'thumbnail': None,
                        }
                    }
                }

                if optional.banner.name:
                    def_banner = absoluteuri.build_absolute_uri(
                        optional.banner.default.url
                    )
                    def_thumbnail = absoluteuri.build_absolute_uri(
                        optional.banner.thumbnail.url
                    )
                    data['service_data']['banners'] = {
                        'default': def_banner,
                        'thumbnail': def_thumbnail,
                    }

                rep['addon_services'].append(data)

                amounts.append(optional.price)

        paid_amount = Decimal(0)
        for trans in instance.transactions.filter(status='paid'):
            paid_amount += trans.amount

        total_amount = round(Decimal(sum(amounts)), 2)
        paid_amount = round(paid_amount, 2)

        if instance.confirmed is True:
            rep['voucher_link'] = absoluteuri.build_absolute_uri(reverse(
                'subscription:subscription-voucher',
                kwargs={
                    'event_pk': instance.event_id,
                    'pk': instance.pk,
                }
            ))

        rep['total_amount'] = total_amount
        rep['paid_amount'] = paid_amount

        return rep


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'lot',
        ]

    def to_representation(self, instance):
        amounts = list()

        rep = dict()
        rep['transactions'] = list()
        rep['amount'] = Decimal(0)

        for trans in instance.transactions.all():
            lot = trans.lot
            sub = trans.subscription

            item = dict()

            item['lot_data'] = {
                'pk': lot.pk,
                'name': lot.name,
                'event': lot.event_id,
                'price': lot.get_calculated_price(),
                'status': lot.status,
                'status_name': lot.get_status_display(),
            }

            if lot.category_id:
                lot_cat = lot.category
                item['lot_data'].update({
                    'category': lot.category_id,
                    'category_data': {
                        'id': lot_cat.pk,
                        'name': lot_cat.name,
                        'active': lot_cat.active,
                        'description': lot_cat.description,
                    }
                })

            person = sub.person
            item['subscription'] = {
                'pk': sub.pk,
                'name': person.name,
                'email': person.email,
                'user': person.user if person.user_id else None,
                'event': sub.event_id,
                'code': sub.code,
                'lot': sub.lot_id,
            }

            item.update(model_to_dict(trans))

            del item['data']

            rep['transactions'].append(item)

            if trans.paid is True:
                amounts.append(trans.amount)

        rep['paid_amount'] = round(Decimal(sum(amounts)), 2)

        return rep
