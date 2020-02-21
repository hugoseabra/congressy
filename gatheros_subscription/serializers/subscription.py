from datetime import datetime
from decimal import Decimal

import absoluteuri
from django.db.transaction import atomic
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import serializers

from gatheros_subscription.models import Subscription
from mailer.services import notify_new_free_subscription
from payment.helpers.payment_helpers import has_open_boleto, \
    get_opened_boleto_transactions


class SubscriptionSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):

        rep = {
            'pk': obj.pk,
            'origin': obj.origin,
            'code': obj.code,
            'accredited': obj.accredited,
            'accredited_on': obj.accredited_on,
            'lot': obj.lot_id,
            'event_count': obj.event_count,
            'completed': obj.completed,
            'test_subscription': obj.test_subscription,
            'status': obj.status,
            'free': obj.free,
            'tag_info': obj.tag_info,
            'tag_group': obj.tag_group,
            'link': absoluteuri.reverse(
                'subscription:subscription-view', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            ),
            'edit_link': None,
            'voucher_link': None,
            'created': obj.created.strftime('%Y-%m-%d %H:%M:%S'),
            'modified': obj.modified.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if obj.confirmed:
            rep['voucher_link'] = absoluteuri.reverse(
                'subscription:subscription-voucher', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            )

        if obj.event.allow_internal_subscription:
            rep['edit_link'] = absoluteuri.reverse(
                'subscription:subscription-edit', kwargs={
                    'event_pk': obj.event.pk,
                    'pk': obj.pk,
                }
            )

        person = obj.person

        rep['person'] = person.pk
        rep['person_data'] = {
            'pk': person.pk,
            'name': person.name,
            'email': person.email,
            'user': person.user_id,
            'city': None,
            'city_international': None,
            'uf': None,
            'cpf': person.cpf,
            'phone': person.phone,
            'international_doc': person.international_doc,
            'institution': None,
            'function': None,
            'birth_date': None,
        }

        if person.city:
            rep['person_data']['city'] = person.city.name
            rep['person_data']['uf'] = person.city.uf

        if person.institution:
            rep['person_data']['institution'] = person.institution

        if person.function:
            rep['person_data']['function'] = person.function

        if person.birth_date:
            rep['person_data']['birth_date'] = \
                person.birth_date.strftime('%Y-%m-%d')

        if person.user_id:
            user = person.user
            rep['person_data']['user_data'] = {
                'pk': user.pk,
                'fist_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login':
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S')
                    if user.last_login else None,
            }

        lot = obj.lot

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
            'date_start': lot.date_start.strftime('%Y-%m-%d %H:%M:%S'),
            'date_end': lot.date_end.strftime('%Y-%m-%d %H:%M:%S'),
            'event_data': {
                'pk': lot.event_id,
                'name': lot.event.name,
                'slug': lot.event.slug,
            },
            'price': lot.get_calculated_price(),
            'liquid_price': lot.get_liquid_price(),
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

        amounts = list()
        amounts.append(lot.get_calculated_price())

        rep['addon_products'] = list()
        addon_products = obj.subscription_products.all()

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
        addon_services = obj.subscription_services.all()

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
        for trans in obj.transactions.filter(status='paid'):
            paid_amount += trans.amount

        total_amount = round(Decimal(sum(amounts)), 2)
        paid_amount = round(paid_amount, 2)

        rep['total_amount'] = total_amount
        rep['paid_amount'] = paid_amount

        rep['has_open_boleto'] = has_open_boleto(obj)

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
            'status',
            'origin',
        ]

    def __init__(self, *args, **kwargs):

        self.subscription_free = None

        instance = kwargs.get('instance')
        if instance:
            # Guarda o estado da inscrição para verificação pós edição.
            self.subscription_free = instance.free is True

        super().__init__(*args, **kwargs)

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
                'last_login':
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S')
                    if user.last_login else None,
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

        rep['has_open_boleto'] = has_open_boleto(instance)

        return rep

    def create(self, validated_data: dict) -> Subscription:
        instance = super().create(validated_data)

        if instance.free is True:
            instance.status = Subscription.CONFIRMED_STATUS

            with atomic():
                instance.save()

                # Inscrições, confirmada, não notificada e completa devem ser
                # notificadas.
                #
                # Inscrições pagas serão notificadas no pagamento.
                if instance.confirmed is True \
                        and instance.completed is True \
                        and instance.notified is False:
                    notify_new_free_subscription(instance.event, instance)
                    instance.notified = True
                    instance.save()

        return instance

    def update(self,
               instance: Subscription,
               validated_data: dict) -> Subscription:

        instance = super().update(instance, validated_data)

        if instance.free is True:
            if self.subscription_free is False:
                # A inscrição não era gratuita antes da edição, mas agora é,
                # então ela mudou de paga para gratuita.
                # Vamos re-notificar o participante com novo código.
                instance.regenerate_code()
                instance.notified = False

            instance.status = Subscription.CONFIRMED_STATUS

        else:
            if self.subscription_free is True:
                # A inscrição era gratuita antes da edição, mas agora não
                # é mais, então ela mudou de gratuita para paga.
                # Vamos re-notificar o participante com novo código.
                instance.regenerate_code()
                instance.notified = False

            if instance.has_debts is True:
                instance.status = Subscription.AWAITING_STATUS

        with atomic():
            instance.save()

            # Inscrições, confirmada, não notificada e completa devem ser
            # notificadas.
            #
            # Inscrições pagas serão notificadas no pagamento.
            if instance.free is True \
                    and instance.confirmed is True \
                    and instance.completed is True \
                    and instance.notified is False:
                notify_new_free_subscription(instance.event, instance)
                instance.notified = True
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
            'date_start': lot.date_start.strftime('%Y-%m-%d %H:%M:%S'),
            'date_end': lot.date_end.strftime('%Y-%m-%d %H:%M:%S'),
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

        rep['has_open_boleto'] = False
        rep['has_open_boleto_same_billing_amount'] = False
        rep['boletos'] = list()

        if has_open_boleto(instance) is True:
            rep['has_open_boleto'] = True

            for boleto in get_opened_boleto_transactions(instance):
                rep['boletos'].append({
                    'pk': str(boleto.pk),
                    'amount': round(boleto.amount, 2),
                    'lot': boleto.lot_id,
                })
                if round(boleto.amount, 2) == total_amount:
                    rep['has_open_boleto_same_billing_amount'] = True

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

        today = datetime.now().date()

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

            item['payer'] = None
            item['payer_data'] = dict()

            if hasattr(trans, 'payer'):
                payer = trans.payer
                benefactor = payer.benefactor

                item['payer'] = benefactor.pk

                item['payer_data'] = {
                    'pk': str(benefactor.pk),
                    'name': benefactor.name,
                    'reference': benefactor.reference,
                    'is_company': benefactor.is_company,
                    'email': benefactor.email,
                    'phone': benefactor.phone,
                    'country': benefactor.country,
                    'cpf': benefactor.cpf,
                    'cnpj': benefactor.cnpj,
                    'doc_type': benefactor.doc_type,
                    'doc_number': benefactor.doc_number,
                }

            if trans.type == trans.BOLETO:
                item['expired'] = trans.boleto_expiration_date <= today
            else:
                item['expired'] = False

            item.update(model_to_dict(trans))

            del item['data']

            rep['transactions'].append(item)

            if trans.paid is True:
                amounts.append(trans.amount)

        rep['paid_amount'] = round(Decimal(sum(amounts)), 2)

        return rep
