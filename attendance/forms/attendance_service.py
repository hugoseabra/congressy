from django import forms
from attendance.models import AttendanceService, AttendanceCategoryFilter, \
    AttendanceServiceFilter, AttendanceProductFilter


class AttendanceServiceForm(forms.ModelForm):
    lot_category_filter = forms.CharField(
        widget=forms.CheckboxSelectMultiple,
        label='Categorias de Lotes',
        required=False,
    )

    product_category_filter = forms.CharField(
        widget=forms.CheckboxSelectMultiple,
        label='Categorias de Opcionais',
        required=False,
    )

    service_category_filter = forms.CharField(
        widget=forms.CheckboxSelectMultiple,
        label='Categorias de Atividades Extras',
        required=False,
    )

    class Meta:
        model = AttendanceService
        fields = (
            'name',
            'event',
            'lot_category_filter',
            'product_filter',
            'service_filter',
        )

    def clean_lot_category_filter(self):
        category_pks = self.cleaned_data.get('lot_category_filter')
        if not category_pks:
            return category_pks

        return AttendanceCategoryFilter.objects.filter(pk__in=category_pks)

    def clean_service_filter(self):
        service_pks = self.cleaned_data.get('service_filters')
        if not service_pks:
            return service_pks

        return AttendanceServiceFilter.objects.filter(pk__in=service_pks)

    def clean_product_filter(self):
        product_pks = self.cleaned_data.get('product_filter')
        if not product_pks:
            return product_pks

        return AttendanceProductFilter.objects.filter(pk__in=product_pks)

    def __create_lot_category_filters(self, service):
        lc_pks = self.data.get('lot_category_filter', [])
        existing_cat_filters = []

        for cat_filter in service.lot_category_filters.all():
            if cat_filter.lot_category.pk in lc_pks:
                existing_cat_filters.append(cat_filter.lot_category.pk)
                continue

            cat_filter.delete()

        cat_filters = service.lot_category_filters

        for cf in cat_filters.exclude(lot_category__pk__in=lc_pks):
            cf.delete()

        for lot_category in self.cleaned_data.get('lot_category_filter'):
            if lot_category.pk in existing_cat_filters:
                continue

            AttendanceCategoryFilter.objects.create(
                attendance_service=service,
                lot_category=lot_category
            )

    def __create_product_filters(self, service):
        product_pks = self.data.get('product_filter', [])
        existing_product_filters = []

        for product_filter in service.product_filters.all():
            if product_filter.product.pk in product_pks:
                existing_product_filters.append(product_filter.product.pk)
                continue

            product_filter.delete()

        product_filters = service.product_filters

        for pf in product_filters.exclude(product__pk__in=product_pks):
            pf.delete()

        for product in self.cleaned_data.get('product_filter'):
            if product.pk in existing_product_filters:
                continue

            AttendanceProductFilter.objects.create(
                attendance_service=service,
                product=product
            )

    def __create_service_filters(self, service):
        service_pks = self.data.get('service_filter', [])
        existing_service_filters = []

        for service_filter in service.service_filters.all():
            if service_filter.service.pk in service_pks:
                existing_service_filters.append(service_filter.service.pk)
                continue

            service_filter.delete()

        service_filters = service.service_filters

        for pf in service_filters.exclude(product__pk__in=service_pks):
            pf.delete()

        for service in self.cleaned_data.get('service_filter'):
            if service.pk in existing_service_filters:
                continue

            AttendanceServiceFilter.objects.create(
                attendance_service=service,
                service=service
            )

    def save(self, commit=True):
        service = super().save(commit)

        self.__create_lot_category_filters(service=service)
        self.__create_product_filters(service=service)
        self.__create_service_filters(service=service)

        return service
