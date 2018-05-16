from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic

from scientific_work.forms import NewWorkForm
from scientific_work.models import Work
from .mixins import WorkViewMixin


class WorkAddView(WorkViewMixin, generic.FormView):
    template_name = "scientific_work/form.html"
    form_class = NewWorkForm

    def form_valid(self, form):
        messages.success(self.request, 'Submissão criada com sucesso.')
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('scientific_work:work-list', kwargs={
            'pk': self.subscription.pk,
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['subscription'] = self.subscription
        return kwargs


class WorkListView(WorkViewMixin, generic.ListView):
    template_name = "scientific_work/list.html"

    def get_queryset(self):
        return Work.objects.filter(subscription=self.subscription)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        must_have = [
            'subscription',
            'modality',
            'area_category',
            'title',
            'summary',
            'keywords',
            'accepts_terms',
        ]

        work_list = context['object_list']
        work_list_with_status = []
        for work in work_list:

            if work.modality == 'artigo':
                if 'banner_file' in must_have:
                    must_have.remove('banner')
                must_have.append('article_file')
            elif work.modality == 'banner':
                if 'article_file' in must_have:
                    must_have.remove('article_file')
                must_have.append('banner_file')
            elif work.modality == 'resumo':
                if 'article_file' in must_have:
                    must_have.remove('article_file')

                if 'banner_file' in must_have:
                    must_have.remove('banner')

            for item in must_have:
                if not getattr(work, item) or work.authors.all().count() < 1:
                    work.status = 'not ready'
                else:
                    work.status = 'ready'
            work_list_with_status.append(work)

        context['object_list'] = work_list_with_status

        return context
