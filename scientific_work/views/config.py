from django.views.generic import TemplateView

from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import AccountMixin
from scientific_work.forms import WorkConfigForm
from scientific_work.models import WorkConfig
from .mixins import EventViewMixin


class ScientificWorkConfigView(TemplateNameableMixin,
                               EventViewMixin,
                               AccountMixin,
                               TemplateView):
    template_name = 'scientific_work/config.html'

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

        try:
            context['work_config'] = self.event.work_config
        except AttributeError:
            context['work_config'] = WorkConfig.objects.create(
                event=self.event)

        context['form'] = WorkConfigForm(instance=self.event.work_config)
        return context
