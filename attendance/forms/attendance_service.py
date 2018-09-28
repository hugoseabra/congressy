from django import forms
from attendance.models import AttendanceService, AttendanceCategoryFilter
from gatheros_subscription.models import LotCategory


class AttendanceServiceForm(forms.ModelForm):
    lot_categories = forms.CharField(
        widget=forms.CheckboxSelectMultiple,
        label='Categorias de Lotes',
        required=False,
    )

    class Meta:
        model = AttendanceService
        fields = (
            'name',
            'event',
            'lot_categories',
            'checkout_enabled',
            'with_certificate'
        )

    def clean_lot_category_filter(self):
        category_pks = self.cleaned_data.get('lot_categories')
        if not category_pks:
            return category_pks

        return AttendanceCategoryFilter.objects.filter(pk__in=category_pks)

    def _create_lot_category_filters(self, service):
        print('gfdfhgsfad')
        lc_pks = self.data.getlist('category_list', [])
        lc_pks = list(map(int, lc_pks))
        existing_cat_filters = []

        if lc_pks:
            for cat_filter in service.lot_category_filters.all():
                if cat_filter.lot_category.pk in lc_pks:
                    existing_cat_filters.append(cat_filter.lot_category.pk)
                    continue

                cat_filter.delete()

            cat_filters = service.lot_category_filters

            for cf in cat_filters.exclude(lot_category__pk__in=lc_pks):
                cf.delete()

            for lot_category in LotCategory.objects.filter(pk__in=lc_pks):
                if lot_category.pk in existing_cat_filters:
                    continue

                AttendanceCategoryFilter.objects.create(
                    attendance_service=service,
                    lot_category=lot_category
                )
        else:
            for lot_category in LotCategory.objects.filter(event_id=service.event_id):
                AttendanceCategoryFilter.objects.create(
                    attendance_service=service,
                    lot_category=lot_category
                )

    def save(self, commit=True):
        service = super().save(commit)
        self._create_lot_category_filters(service=service)

        return service