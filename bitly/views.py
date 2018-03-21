from django.views.generic import TemplateView


class BitlyView(TemplateView):
    template_name = 'bitly/test.html'
