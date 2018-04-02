from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
import json
from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import EventViewMixin, AccountMixin
from gatheros_subscription.forms import SurveyForm
from gatheros_subscription.models import EventSurvey
from survey.constants import TYPE_LIST as QUESTION_TYPE_LIST
from survey.forms import QuestionForm, SurveyForm as FullSurveyForm
from survey.models import Survey, Question


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
        context['form'] = QuestionForm(survey=self.survey)
        context['full_survey_form'] = FullSurveyForm(
            survey=self.survey)

        return context

    def post(self, request, *args, **kwargs):

        if self.request.is_ajax():

            action = self.request.POST.get('action')
            question_id = self.request.POST.get('question_id')

            if action == 'delete':

                try:
                    question = Question.objects.get(name=question_id)
                    question.delete()
                except Question.DoesNotExist:
                    return HttpResponse(status=404)

                return HttpResponse(status=200)
            elif action == 'update_order':

                new_order = json.loads(self.request.POST.get(
                    'new_order'))

                counter = 1
                try:
                    for question_name in new_order:
                        question = Question.objects.get(survey=self.survey,
                                                        name=question_name)
                        question.order = counter
                        question.save()
                        counter += 1

                    return HttpResponse(status=200)

                except Question.DoesNotExist:
                    return HttpResponse(status=404)
            elif action == 'update_required':
                set_to = self.request.POST.get('setTo')
                try:
                    question = Question.objects.get(name=question_id)
                except Question.DoesNotExist:
                    return HttpResponse(status=404)

                if set_to == "True":
                    question.required = True
                elif set_to == "False":
                    question.required = False
                else:
                    return HttpResponse(status=500)

                question.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=500)

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

            question_data = {
                'survey': self.survey.pk,
                'type': request.POST.get('question_type'),
                'name': request.POST.get('name'),
                'label': request.POST.get('name'),
                'help_text': request.POST.get('help_text'),
                'intro': request.POST.get('intro', False),
                'options': request.POST.get('options')
            }

            question_form = QuestionForm(survey=self.survey,
                                         data=question_data)

            if question_form.is_valid():
                question_form.save()
                messages.success(
                    self.request,
                    "Pergunta criada com sucesso!"
                )
            else:
                messages.error(
                    self.request,
                    "Corrija os erros abaixo."
                )

        return redirect(reverse_lazy('subscription:survey-edit', kwargs={
            'event_pk': self.event.pk,
            'survey_pk': self.survey.pk,
        }))

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

            context = self.get_queryset()
            context['form'] = form
            return self.render_to_response(context=context)

        return redirect(reverse_lazy('subscription:survey-list', kwargs={
            'event_pk': self.event.pk,
        }))


class EventSurveyDeleteView(EventViewMixin, AccountMixin, generic.DeleteView, ):
    """
        View responsavel por deletar questionarios.
    """
    template_name = 'survey/delete.html'
    model = EventSurvey

    def get_success_url(self):
        return reverse_lazy('subscription:survey-list', kwargs={
            'event_pk': self.event.pk,
        })
