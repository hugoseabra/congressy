from django.contrib import admin
from django.db.models import Count, Q

from gatheros_event.models import Event
from .models import (
    Answer,
    DefaultField,
    DefaultFieldOption,
    Field,
    FieldOption,
    Form,
    Lot,
    Subscription,
)


@admin.register(DefaultField)
class DefaultFieldAdmin(admin.ModelAdmin):
    list_display = (
        'label',
        'field_type',
        'required',
        'with_options',
        'pk'
    )

    fields = [
        'label',
        'name',
        'field_type',
        'required',
        'select_intro',
        'instruction',
        'placeholder',
        'default_value',
        'active',
    ]


class DefaultFieldWithOptionFilter(admin.SimpleListFilter):
    title = 'Campo com opções'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'field__label'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        fields = DefaultField.objects.filter(with_options=True)

        return [(field.pk, field.label) for field in fields]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            queryset = queryset.filter(field__pk=self.value())

        return queryset


@admin.register(DefaultFieldOption)
class DefaultFieldOptionAdmin(admin.ModelAdmin):
    list_filter = (DefaultFieldWithOptionFilter,)
    list_display = (
        'name',
        'get_field_label',
        'pk'
    )
    ordering = ['field', 'name', 'value']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "field":
            kwargs["queryset"] = DefaultField.objects.filter(
                with_options=True
            ).all()

        return super(DefaultFieldOptionAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def get_field_label(self, instance):
        return '{} [ {} ]'.format(
            instance.field.label,
            instance.field.get_field_type_display()
        )

    get_field_label.__name__ = 'campo'


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    search_fields = (
        'label',
        'name',
        'forms__event__name',
        'organization__name',
    )
    list_display = (
        'organization',
        'get_events',
        'label',
        'name',
        'field_type',
        'required',
        'form_default_field',
        'with_options',
        'num_forms',
        'pk'
    )
    fields = [
        'organization',
        'forms',
        'label',
        'name',
        'field_type',
        'required',
        'select_intro',
        'instruction',
        'placeholder',
        'default_value',
        'active',
        'with_options',
        'form_default_field',
    ]
    readonly_fields = ['name', 'form_default_field', 'with_options']

    def get_events(self, instance):
        events = [
            '<div style="padding:3px 0">- ' + form.event.name + '</div>'
            for form in instance.forms.all()
        ]

        return "".join(events)

    def num_forms(self, instance):
        return instance.forms.count()

    num_forms.__name__ = '# Forms'
    get_events.__name__ = 'Eventos'
    get_events.allow_tags = True


@admin.register(FieldOption)
class FieldOptionAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
        'field__label',
        'field__name',
        'field__forms__event__name',
    )
    list_display = (
        'name',
        'value',
        'get_field_label',
        'pk'
    )
    ordering = ['field', 'name', 'value']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "field":
            kwargs["queryset"] = Field.objects.filter(with_options=True).all()

        return super(FieldOptionAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def get_field_label(self, instance):
        return '{} [ {} ]'.format(
            instance.field.label,
            instance.field.get_field_type_display()
        )

    get_field_label.__name__ = 'campo'


class FieldInline(admin.StackedInline):
    verbose_name = 'Campo'
    verbose_name_plural = 'Campos'
    model = Field.forms.through
    extra = 0


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    pk = None
    inlines = (FieldInline,)

    def get_form(self, request, obj=None, **kwargs):
        self.pk = None
        if obj:
            self.pk = obj.id

        return super(FormAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if not self.pk and db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter(form=None).exclude(
                subscription_type=Event.SUBSCRIPTION_DISABLED
            )

        return super(FormAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def has_additional_fields(self, instance):
        return instance.has_additional_fields()

    has_additional_fields.__name__ = 'campos adicionais'
    has_additional_fields.boolean = True

    list_display = ('event', 'has_additional_fields',)


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'event',
        'price',
        'date_start',
        'date_end',
        'get_percent_completed',
        'get_percent_attended',
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

    def get_percent_completed(self, instance):
        if not instance.limit:
            return 'Livre'

        remaining = instance.limit - instance.subscriptions.count()
        percent = '{0:.2f}'.format(100 - instance.percent_completed)
        return '{} ({}%)'.format(remaining, percent)

    def get_percent_attended(self, instance):
        queryset = instance.subscriptions
        return '{}/{} ({}%)'.format(
            queryset.filter(attended=True).count(),
            queryset.count(),
            '{0:.2f}'.format(instance.percent_attended)
        )

    get_percent_completed.__name__ = 'Vagas restantes'
    get_percent_attended.__name__ = 'Credenciados'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
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
                is_simple = \
                    event.subscription_type == Event.SUBSCRIPTION_SIMPLE
                has_lots = event.lots.count() > 0
                if is_simple and has_lots:
                    continue

            kwargs["queryset"] = events

        return super(LotAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


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


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'get_field', 'get_value']
    ordering = ['field__label', 'subscription__person']
    list_filter = ('field__forms__event',)
    search_fields = (
        'subscription__person__name',
        'subscription__event__name',
        'field__name',
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subscription":
            kwargs["queryset"] = Subscription.objects \
                .annotate(num_answers=Count('answers')) \
                .filter(event__form__fields__form_default_field=False) \
                .order_by('event__name') \
                .distinct()

        if db_field.name == "field":
            kwargs["queryset"] = Field.objects.filter(
                form_default_field=False
            ).order_by('-required')

        return super(AnswerAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def get_field(self, instance):
        field = instance.field.label
        field += ' [ ' + instance.field.get_field_type_display() + ' ]'
        return field

    def get_value(self, instance):
        return instance.get_display_value()

    get_field.__name__ = 'campo'
    get_value.__name__ = 'valor'
