# pylint: disable=W0222
"""
Django Admin para Trabalhos cientificos
"""
from django.contrib import admin

from .models import AreaCategory, Author, Work, WorkConfig


@admin.register(AreaCategory)
class AreaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('work', 'name',)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = (
        'modality',
        'area_category',
        'title',
        'published',
    )


@admin.register(WorkConfig)
class WorkConfigAdmin(admin.ModelAdmin):
    list_display = (
        'date_start',
        'date_end',
        'presenting_type',
        'allow_unconfirmed_subscriptions',
    )
