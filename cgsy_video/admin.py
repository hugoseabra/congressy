# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import VideoConfig


@admin.register(VideoConfig)
class VideoConfigAdmin(admin.ModelAdmin):
    list_display = ('event', 'token', 'project_pk')
    search_fields = ('event__name', 'token', 'project_pk')
    raw_id_fields = ('event',)
