from django.contrib import admin

from certificate import forms

@admin.register(forms.Certificate)
class CertificateAdmin(admin.ModelAdmin):
    form = forms.CertificateForm

    fieldsets = (
        ('Texto Principal', {
            'fields': (
                'event',
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