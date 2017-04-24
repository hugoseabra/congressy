import json

from django.contrib import admin
from django.db.models import Count, Q

from gatheros_event.models import Event
from .models import Answer, Field, FieldOption, Form, Lot, Subscription


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('form', 'order', 'label', 'type', 'required', 'form_default_field', 'pk')


@admin.register(FieldOption)
class FieldOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'get_field_label', 'get_event_form', 'pk')
    ordering = ['field', 'name', 'value']

    def get_field_label(self, instance):
        return '{} [{}]'.format(instance.field.label, instance.field.type)

    def get_event_form(self, instance):
        return instance.field.form

    get_field_label.__name__ = 'campo'
    get_event_form.__name__ = 'formulário'


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'date_start', 'date_end', 'private', 'internal', 'pk')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            events = Event.objects.annotate(num_lots=Count('lots')).filter(
                Q(subscription_type=Event.SUBSCRIPTION_SIMPLE, num_lots__exact=0) |
                Q(subscription_type=Event.SUBSCRIPTION_BY_LOTS)
            )

            for event in events:
                if event.subscription_type == Event.SUBSCRIPTION_SIMPLE and event.lots.count() > 0:
                    continue

            kwargs["queryset"] = events

        return super(LotAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('person', 'count', 'lot', 'code', 'attended',)
    readonly_fields = ['event', 'code', 'count', 'attended', 'attended_on', 'synchronized']
    ordering = ('lot', 'count', 'person',)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter('')

        return super(FormAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_additional_fields(self, instance):
        return instance.has_additional_fields

    has_additional_fields.__name__ = 'campos adicionais'
    has_additional_fields.boolean = True

    list_display = ('event', 'has_additional_fields',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'field', 'get_value']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "field":
            kwargs["queryset"] = Field.objects.filter(form_default_field=False)
        if db_field.name == "subscription":
            kwargs["queryset"] = Subscription.objects.filter(event__form__fields__form_default_field=False).distinct()

        return super(AnswerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_value(self, instance):
        data = json.loads(instance.value)
        has_options = instance.field.options.count() > 0

        def format_result(dict, has_options=False):
            if has_options:
                return dict['name']
            else:
                return dict['value']

        if type(data) is list:
            result = []
            for v in data:
                result.append(format_result(v, has_options))
            return ', '.join(result)
        else:
            return format_result(data, has_options)

    get_value.__name__ = 'valor'
