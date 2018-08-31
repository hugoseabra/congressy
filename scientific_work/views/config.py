from datetime import datetime

from django.views.generic import TemplateView

from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import AccountMixin, EventViewMixin
from scientific_work.forms import WorkConfigForm
from scientific_work.models import WorkConfig


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

    def _get_or_create_work_config(self):

        try:
            return self.event.work_config
        except AttributeError:
            return WorkConfig.objects.create(event=self.event)

    def _get_not_submittable_reasons(self):
        reasons = []

        work_config = self._get_or_create_work_config()
        if not work_config.date_start and not work_config.date_end:
            reasons.append('Prazo de submissão não está configurado.')
        elif work_config.date_start and not work_config.date_end:
            reasons.append('Data de inicio para o prazo de submissão não está '
                           'configurado.')
        elif not work_config.date_start and work_config.date_end:
            reasons.append('Data de inicio para o prazo de submissão não está '
                           'configurado.')

        area_categories = self.event.area_categories.all()
        if not area_categories.count() > 0:
            reasons.append('Nenhuma áreas temática configurada')

        now = datetime.now()
        if work_config.date_start and work_config.date_end:
            if work_config.date_end < now:
                reasons.append('Já se passou o prazo de submissão')
            elif work_config.date_start > now:
                reasons.append('Ainda não se iniciou o prazo para a submissão')

        return reasons

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['work_config'] = self._get_or_create_work_config()
        context['has_inside_bar'] = True
        context['active'] = 'scientific_work'
        context['event'] = self.event
        context['area_categories'] = self._get_area_categories()

        reasons = self._get_not_submittable_reasons()
        context['is_submittable'] = self.event.work_config.is_submittable
        context['not_submittable_reasons'] = reasons

        context['form'] = WorkConfigForm(instance=self.event.work_config)
        return context
