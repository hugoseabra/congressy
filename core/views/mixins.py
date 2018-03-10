from django.views.generic.base import TemplateResponseMixin


class TemplateNameableMixin(TemplateResponseMixin):
    def get_template_names(self):
        template = self.request.GET.get('template_name')
        if template:
            if not template.endswith('.html'):
                template += '.html'
            return [template]

        return super().get_template_names()
