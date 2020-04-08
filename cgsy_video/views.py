from django.views import generic

from gatheros_event.views.mixins import EventViewMixin


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

        return context


class CategoriesView(EventViewMixin, generic.TemplateView):
    template_name = 'cgsy_video/category_list.html'

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.videos is True

        return can is True and feature_active is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'videos'

        return context


class PlaylistsView(EventViewMixin, generic.TemplateView):
    template_name = 'cgsy_video/playlist_list.html'

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.videos is True

        return can is True and feature_active is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'videos'

        return context
