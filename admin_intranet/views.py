from django.views.generic import TemplateView

from gatheros_event.views.mixins import AccountMixin


class IndexView(AccountMixin, TemplateView):
    template_name = 'admin/index.html'
