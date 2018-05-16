from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from scientific_work.models import Author, Work
from .mixins import WorkViewMixin


class AuthorPartialListView(WorkViewMixin, generic.ListView):
    template_name = "scientific_work/author_modal_list.html"
    work = None

    def dispatch(self, request, *args, **kwargs):
        work_pk = self.kwargs.get('pk')
        if not work_pk:
            messages.error(self.request, 'Não foi possivel resgatar a '
                                         'submissão.')
            return redirect(reverse_lazy('front:start'))

        self.work = get_object_or_404(Work, pk=work_pk)

        response = super().dispatch(request, *args, **kwargs)

        return response

    def get_queryset(self):
        return Author.objects.filter(work=self.work)
