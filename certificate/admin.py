from django.contrib import admin

from certificate import forms
from certificate.models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    form = forms.CertificateForm
    raw_id_fields = ['event']
    fieldsets = (
        ('Texto Principal', {
            'fields': (
                'event',
                'background_image',
                'text_content',
                'text_font_size',
                'text_position_x',
                'text_position_y',
                'text_width',
                'text_height',
                'text_line_height',
            ),
        }),
        ('Título', {
            'fields': (
                'title_content',
                'title_font_size',
                'title_position_x',
                'title_position_y',
                'title_hide',
            ),
        }),
        ('Data', {
            'fields': (
                'date_font_size',
                'date_position_x',
                'date_position_y',
                'date_hide',
            ),
        }),
    )

    def has_add_permission(self, request):
        return False
