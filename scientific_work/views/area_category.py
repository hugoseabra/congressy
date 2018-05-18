from django.views.generic import TemplateView

from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import AccountMixin
from .mixins import EventViewMixin


class AreaCategoryConfigView(TemplateNameableMixin, EventViewMixin,
                             AccountMixin,
                             TemplateView):
    template_name = 'scientific_work/area_config_form.html'

    def _get_area_categories(self):
        categories = None

        if self.event.area_categories.all().count() > 0:
            categories = self.event.area_categories.all()

        return categories

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'scientific_work'
        context['event'] = self.event
        context['area_categories'] = self._get_area_categories()

        return context
