import json

from django.contrib import admin
from django.db.models import Count, Q

from gatheros_event.models import Event
from .models import Answer, Field, FieldOption, Form, Lot, Subscription, DefaultField


@admin.register(DefaultField)
class DefaultFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'type', 'required', 'pk')
    fields = [
        'name',
        'label',
        'type',
        'order',
        'required',
        'instruction',
        'placeholder',
        'default_value',
        'active',
    ]


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = (
        'form',
        'order',
        'label',
        'type',
        'required',
        'form_default_field',
        'with_options',
        'pk'
    )
    readonly_fields = ['form_default_field', 'with_options']
    fields = [
        'form',
        'name',
        'label',
        'type',
        'order',
        'required',
        'instruction',
        'placeholder',
        'default_value',
        'active',
        'with_options',
        'form_default_field',
    ]


@admin.register(FieldOption)
class FieldOptionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'value',
        'get_field_label',
        'get_event_form',
        'pk'
    )
    ordering = ['field', 'name', 'value']

    def formfield_for_foreignkey( self, db_field, request, **kwargs ):
        if db_field.name == "field":
            kwargs["queryset"] = Field.objects.filter(with_options=True).all()

        return super(FieldOptionAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def get_field_label( self, instance ):
        return '{} [ {} ]'.format(
            instance.field.label,
            instance.field.get_type_display()
        )

    def get_event_form( self, instance ):
        return instance.field.form

    get_field_label.__name__ = 'campo'
    get_event_form.__name__ = 'formulário'


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'event',
        'price',
        'date_start',
        'date_end',
        'private',
        'internal',
        'pk'
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'event',
                'date_start',
                'date_end',
                'limit',
                'private',
                'internal',
            ),
        }),
        ('Preços e Formas de recebimento', {
            'fields': (
                'promo_code',
                'price',
                'tax',
                'discount',
                'discount_type',
                'transfer_tax',
            ),
        }),
    )

    def formfield_for_foreignkey( self, db_field, request, **kwargs ):
        if db_field.name == "event":
            events = Event.objects.annotate(num_lots=Count('lots')).filter(
                Q(
                    subscription_type=Event.SUBSCRIPTION_SIMPLE,
                    num_lots__exact=0
                ) | Q(
                    subscription_type=Event.SUBSCRIPTION_BY_LOTS
                )
            )

            for event in events:
                if event.subscription_type == Event.SUBSCRIPTION_SIMPLE and event.lots.count() > 0:
                    continue

            kwargs["queryset"] = events

        return super(LotAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('person', 'count', 'lot', 'code', 'attended',)
    readonly_fields = [
        'event',
        'code',
        'count',
        'attended',
        'attended_on',
        'synchronized'
    ]
    ordering = ('lot', 'count', 'person',)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    def get_form( self, request, obj=None, **kwargs ):
        self.pk = None
        if obj:
            self.pk = obj.id

        return super(FormAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey( self, db_field, request, **kwargs ):

        if not self.pk and db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter(form=None).exclude(
                subscription_type=Event.SUBSCRIPTION_DISABLED
            )

        return super(FormAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def has_additional_fields( self, instance ):
        return instance.has_additional_fields

    has_additional_fields.__name__ = 'campos adicionais'
    has_additional_fields.boolean = True

    list_display = ('event', 'has_additional_fields',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['get_event', 'get_subscription', 'get_field', 'get_value']
    ordering = ['field__form', 'subscription__person', 'field__order']

    def formfield_for_foreignkey( self, db_field, request, **kwargs ):
        if db_field.name == "subscription":
            kwargs["queryset"] = Subscription.objects \
                .annotate(num_answers=Count('answers')) \
                .filter(event__form__fields__form_default_field=False) \
                .order_by('event__name') \
                .distinct()

        if db_field.name == "field":
            kwargs["queryset"] = Field.objects.filter(
                form_default_field=False
            ).order_by('form__event', '-required')

        return super(AnswerAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def get_event( self, instance ):
        return instance.field.form

    def get_subscription( self, instance ):
        return instance.subscription.person

    def get_field( self, instance ):
        field = instance.field.label
        field += ' [ '+instance.field.get_type_display()+' ]'
        return field

    def get_value( self, instance ):
        return instance.get_display_value()

    get_event.__name__ = 'event'
    get_subscription.__name__ = 'inscrição'
    get_field.__name__ = 'campo'
    get_value.__name__ = 'valor'
