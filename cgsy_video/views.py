from django.conf import settings
from django.views import generic

from gatheros_event.views.mixins import EventViewMixin
from cgsy_video.workers import create_video_config


class VideosView(EventViewMixin, generic.TemplateView):
    template_name = 'cgsy_video/video_list.html'

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.videos is True

        return can is True and feature_active is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'videos'

        enabled = hasattr(self.event, 'video_config')

        context['videos_enabled'] = enabled
        context['API_BASE_URL'] = settings.CGSY_VIDEOS_API_URL
        context['API_TOKEN'] = None
        context['PROJECT_PK'] = None

        if enabled is False:
            create_video_config.delay(self.event.pk)
        else:
            context['API_TOKEN'] = self.event.video_config.token
            context['PROJECT_PK'] = self.event.video_config.project_pk

        return context


class CategoriesView(EventViewMixin, generic.TemplateView):
    template_name = 'cgsy_video/category_list.html'

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.videos is True
        enabled = hasattr(self.event, 'video_config')

        return can is True and feature_active is True and enabled

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'videos'

        context['API_BASE_URL'] = settings.CGSY_VIDEOS_API_URL
        context['API_TOKEN'] = self.event.video_config.token
        context['PROJECT_PK'] = self.event.video_config.project_pk

        return context


class PlaylistsView(EventViewMixin, generic.TemplateView):
    template_name = 'cgsy_video/playlist_list.html'

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.videos is True

        enabled = self.event.feature_configuration.feature_videos

        return can is True and feature_active is True and enabled is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'videos'

        return context
