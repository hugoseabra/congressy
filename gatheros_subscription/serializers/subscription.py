from decimal import Decimal

import absoluteuri
from django.forms import model_to_dict
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

        lot = instance.lot
        rep['lot_data'] = {
            'pk': lot.pk,
            'name': lot.name,
            'event': lot.event_id,
            'event_data': {
                'pk': lot.event_id,
                'name': lot.event.name,
                'slug': lot.event.slug,
            },
            'category': lot.category_id,
            'category_data': {
                'pk': lot.category.pk,
                'name': lot.category.name,
                'description': lot.category.description,
            }
        }

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

        return rep


class SubscriptionBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'lot',
        ]

    def to_representation(self, instance):
        lot = instance.lot
        amounts = list()

        rep = dict()

        survey = None
        survey_data = dict()

        if lot.event_survey_id:
            survey = lot.event_survey.survey
            survey_data = {
                'pk': survey.pk,
                'name': survey.name,
                'description': survey.description,
            }

        rep['lot'] = {
            'pk': lot.pk,
            'name': lot.name,
            'event': lot.event_id,
            'price': lot.get_calculated_price(),
            'survey': survey.pk if survey else None,
            'survey_data': survey_data
        }
        amounts.append(lot.get_calculated_price())

        if lot.category_id:
            rep['lot'].update({
                'category': {
                    'pk': lot.category_id,
                    'name': lot.category.name,
                    'description': lot.category.description,
                }
            })

        addon_products = instance.subscription_products.all()

        rep['addon_products'] = list()
        if addon_products.count():
            for addon_sub in addon_products:
                optional = addon_sub.optional
                rep['addon_products'].append({
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
                })

                if optional.banner.name:
                    rep['addon_products']['product_data']['banners'] = {
                        'default': optional.banner.default.url,
                        'thumbnail': optional.banner.thumbnail.url,
                    }

                amounts.append(optional.price)

        addon_services = instance.subscription_services.all()

        rep['addon_services'] = list()
        if addon_services.count():
            for addon_sub in addon_services:
                optional = addon_sub.optional
                rep['addon_services'].append({
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
                })

                if optional.banner.name:
                    rep['addon_services']['service_data']['banners'] = {
                        'default': optional.banner.default.url,
                        'thumbnail': optional.banner.thumbnail.url,
                    }

                amounts.append(optional.price)

        rep['total_amount'] = round(Decimal(sum(amounts)), 2)

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
            lot_cat = lot.category
            sub = trans.subscription

            item = dict()

            item['lot_data'] = {
                'pk': lot.pk,
                'name': lot.name,
                'event': lot.event_id,
                'price': lot.get_calculated_price(),
                'category': lot.category_id,
                'category_data': {
                    'id': lot_cat.pk,
                    'name': lot_cat.name,
                    'active': lot_cat.active,
                    'description': lot_cat.description,
                }
            }

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
