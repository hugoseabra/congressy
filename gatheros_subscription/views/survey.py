from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import EventViewMixin, AccountMixin
from gatheros_subscription.forms import SurveyForm
from gatheros_subscription.models import EventSurvey
from survey.constants import TYPE_LIST as QUESTION_TYPE_LIST
from survey.forms import QuestionForm
from survey.models import Survey


class SurveyEditView(EventViewMixin, AccountMixin, generic.TemplateView,
                     TemplateNameableMixin):
    template_name = 'survey/edit.html'
    survey = None

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()
        self.survey = self.get_survey()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['survey'] = self.survey
        context['form'] = QuestionForm

        return context

    def post(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)

        question_type = self.request.POST.get('question_type', None)

        if not question_type:
            messages.error(
                self.request,
                'Você não especificou o tipo de pergunta.'
            )

        elif question_type not in QUESTION_TYPE_LIST:
            messages.error(
                self.request,
                "Esse tipo de pergunta não é permitido."
            )
        else:

            question_form = QuestionForm(data=request.POST)

            # if question_form.is_valid():
            #
            #     model_data = {
            #         'type': question_type,
            #         'title': question_form.cleaned_data.get('title'),
            #
            #     }
            #
            #     question_model_form = QuestionModelForm(data=question_form)
            #     print('hell ya')

        return self.render_to_response(context)

    def get_survey(self):
        """ Resgata questionário do contexto da view. """

        if self.survey:
            return self.survey

        self.survey = get_object_or_404(
            Survey,
            pk=self.kwargs.get('survey_pk')
        )
        return self.survey


class SurveyListView(EventViewMixin, AccountMixin, generic.ListView, ):
    """
        View responsavel pela listagens dos formularios pertencentes a um
        evento.
    """
    template_name = 'survey/list.html'

    model = EventSurvey
    ordering = ['event__name']

    def get_queryset(self):
        """Surveys a exibir são de acordo com o evento"""
        query_set = super(SurveyListView, self).get_queryset()
        return query_set.filter(event=self.event)

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['form'] = SurveyForm(event=self.event)
        return context

    def post(self, *args, **kwargs):

        form = SurveyForm(data=self.request.POST, event=self.event)

        if form.is_valid():

            form.save()

        else:

            messages.error(
                self.request,
                "Corrija os erros abaixo."
            )

        return redirect(reverse_lazy('subscription:survey-list', kwargs={
            'event_pk': self.event.pk,
        }))
