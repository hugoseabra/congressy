import json

from django.contrib import admin
from .models import Form, Field, FieldOption, Lot, Subscription, Answer


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('form', 'order', 'label', 'type', 'required', 'form_default_field', 'pk')


@admin.register(FieldOption)
class FieldOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'get_field_label', 'get_form', 'pk')

    def get_field_label(self, instance):
        return '{} [{}]'.format(instance.field.label, instance.field.type)

    def get_form(self, instance):
        return instance.field.form

    get_field_label.__name__ = 'campo'
    get_form.__name__ = 'formulário'


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'date_start', 'date_end', 'private', 'internal', 'pk')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('person', 'count', 'lot', 'code', 'attended',)
    readonly_fields = ['event', 'code', 'count', 'attended', 'attended_on', 'synchronized']
    ordering = ('lot', 'count', 'person',)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
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