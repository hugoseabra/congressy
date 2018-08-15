import json
from ast import literal_eval

from django.contrib import messages
from django.db.models.functions import Lower
from django.db.transaction import atomic
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views import generic

from core.util import represents_int
from core.views.mixins import TemplateNameableMixin
from gatheros_event.views.mixins import EventViewMixin, AccountMixin
from gatheros_subscription.forms import EventSurveyForm
from gatheros_subscription.models import EventSurvey, Lot
from survey.api import SurveySerializer
from survey.constants import TYPE_LIST as QUESTION_TYPE_LIST
from survey.forms import QuestionForm, SurveyAnswerForm
from survey.models import Question
from .mixins import SurveyFeatureFlagMixin


class SurveyEditView(SurveyFeatureFlagMixin,
                     EventViewMixin,
                     generic.TemplateView,
                     TemplateNameableMixin):
    template_name = 'survey/edit.html'
    survey = None
    event_survey = None

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()
        self.event_survey = EventSurvey.objects.get(
            pk=self.kwargs.get('survey_pk'),
            event=self.event,
        )
        self.survey = self.event_survey.survey

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['survey'] = self.survey
        context['has_inside_bar'] = True
        context['active'] = 'form-personalizado'
        context['form'] = QuestionForm(survey=self.survey)
        context['lots'] = self._get_selected_lots()
        context['full_survey_form'] = SurveyAnswerForm(
            survey=self.survey)

        return context

    def post(self, request, *args, **kwargs):

        if self.request.is_ajax():

            action = self.request.POST.get('action')
            question_id = self.request.POST.get('question_id')

            if not action or not question_id:
                HttpResponse(
                    "Sem id({}) ou sem ação({})".format(question_id, action),
                    status=500, )

            if action == 'delete':

                question = get_object_or_404(Question,
                                             survey=self.survey,
                                             pk=int(question_id))
                question.delete()
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
                    question = Question.objects.get(name=question_id,
                                                    survey=self.survey)
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

            elif action == 'edit':

                try:
                    question = Question.objects.get(pk=question_id,
                                                    survey=self.survey)
                except Question.DoesNotExist:
                    return HttpResponse(status=404)

                data = literal_eval(request.POST.get('question'))

                question_data = {
                    'name': data.get('name_edit', question.name),
                    'label': data.get('name_edit', question.label),
                    'help_text': data.get('help_text_edit',
                                          question.help_text),
                    'intro': bool(data.get('intro_edit', False)),
                    'options': data.get('options_edit', question.options),
                    'survey': self.survey.pk,
                    'type': question.type,
                }

                question_form = QuestionForm(
                    data=question_data,
                    instance=question,
                    survey=self.survey,
                )

                if question_form.is_valid():
                    question_form.save()
                    return HttpResponse(status=200)

                return HttpResponse(status=500)

            elif action == 'duplicate':

                question = get_object_or_404(
                    Question,
                    pk=question_id,
                    survey=self.survey
                )

                with atomic():
                    options = question.options.all().order_by('pk') \
                        if question.has_options \
                        else []

                    question.pk = None
                    question.label = 'Cópia - {}'.format(question.label)
                    question.name = slugify(question.label)
                    question.save()

                    for option in options:
                        option.pk = None
                        option.question = question
                        option.save()

                return HttpResponse(status=200)

            elif action == 'change_type':

                new_type = self.request.POST.get('new_type')

                if new_type not in QUESTION_TYPE_LIST:
                    return HttpResponse(status=500)

                question = get_object_or_404(
                    Question,
                    pk=question_id,
                    survey=self.survey
                )

                question.type = new_type
                question.save()

                return HttpResponse(status=200)

            elif action == 'deactivate':
                question = get_object_or_404(
                    Question,
                    pk=question_id,
                    survey=self.survey
                )

                if question.active is True:
                    question.active = False
                    question.save()

                    return HttpResponse(status=200)

            elif action == 'activate':
                question = get_object_or_404(
                    Question,
                    pk=question_id,
                    survey=self.survey
                )

                if question.active is False:
                    question.active = True
                    question.save()
                    return HttpResponse(status=200)

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
                'active': True,
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
                for key, err in question_form.errors.items():
                    messages.error(
                        self.request,
                        err[0]
                    )

        return redirect(reverse_lazy('subscription:survey-edit', kwargs={
            'event_pk': self.event.pk,
            'survey_pk': self.event_survey.pk,
        }))

    def _get_selected_lots(self):
        lots_list = []
        all_lots = self.event.lots.all().order_by(Lower('name'))
        selected_lots = self.event_survey.lots.all()

        for lot in all_lots:
            if lot in selected_lots:
                lots_list.append({'lot': lot, 'selected': True})
            else:
                lots_list.append({'lot': lot, 'selected': False})

        return lots_list


class SurveyListView(SurveyFeatureFlagMixin,
                     EventViewMixin,
                     generic.ListView):
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
        context['form'] = EventSurveyForm(event=self.event)
        return context


class EventSurveyCreateView(SurveyFeatureFlagMixin,
                            EventViewMixin):
    def post(self, request, *args, **kwargs):
        data = request.POST.copy()

        form = EventSurveyForm(data=data, event=self.event)

        if form.is_valid():
            instance = form.save()
            serialized_obj = SurveySerializer(instance)

            object_dict = serialized_obj.data
            url = reverse(
                'subscription:survey-edit', kwargs={
                    'event_pk': self.event.pk,
                    'survey_pk': instance.pk
                })
            object_dict.update({'url': url})
            object_json = json.dumps(object_dict)

            return JsonResponse(object_json, status=201, safe=False)

        return HttpResponse(status=400)


class EventSurveyDuplicateView(SurveyFeatureFlagMixin,
                               EventViewMixin):
    def post(self, request, *args, **kwargs):

        event_survey = get_object_or_404(
            EventSurvey,
            pk=self.kwargs.get('survey_pk')
        )

        with atomic():
            survey = event_survey.survey
            questions = survey.questions.all().order_by('pk')

            new_survey = survey

            # Duplicando survey
            new_survey.pk = None
            new_survey.name = 'Cópia - {}'.format(new_survey.name)
            new_survey.save()

            new_event_survey = event_survey
            new_event_survey.pk = None
            new_event_survey.survey = new_survey
            new_event_survey.save()

            # Duplicando perguntas
            for question in questions:
                options = question.options.all().order_by('pk') \
                    if question.has_options \
                    else []

                new_question = question
                new_question.pk = None
                new_question.survey = new_survey
                new_question.save()

                # Duplicando opções
                for option in options:
                    new_option = option
                    new_option.pk = None
                    new_option.question = new_question
                    new_option.save()

        return HttpResponse(status=200)


class EventSurveyDeleteAjaxView(SurveyFeatureFlagMixin,
                                EventViewMixin,
                                generic.TemplateView):
    """
        View responsavel por deletar questionarios.
    """
    template_name = 'survey/delete.html'

    def post(self, request, *args, **kwargs):

        event_survey_id = request.POST.get('event_survey_id')

        if event_survey_id:
            event_survey = get_object_or_404(EventSurvey, pk=event_survey_id)

            survey = event_survey.survey
            event_survey.delete()
            survey.delete()

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)

    def get_success_url(self):
        return reverse_lazy('subscription:survey-list', kwargs={
            'event_pk': self.event.pk,
        })


class EventSurveyEditAjaxView(SurveyFeatureFlagMixin,
                              EventViewMixin):
    """
        View responsavel por editar questionarios.
    """

    def post(self, request, *args, **kwargs):

        event_survey_id = request.POST.get('event_survey_id')

        edited_title = request.POST.get('survey_edit_title')
        edited_description = request.POST.get('survey_edit_description')

        if event_survey_id:
            event_survey = get_object_or_404(EventSurvey, pk=event_survey_id)

            survey = event_survey.survey

            if edited_title:
                survey.name = edited_title

            if edited_description:
                survey.description = edited_description

            survey.save()

            return HttpResponse(status=200)

        return HttpResponse(status=500)


class EventSurveyLotsEditAjaxView(SurveyFeatureFlagMixin,
                                  EventViewMixin):
    event_survey = None

    def dispatch(self, request, *args, **kwargs):

        if 'event_survey' not in request.POST:
            raise Exception('Não foi passado um event_survey dentro do JSON.')

        event_survey = request.POST.get('event_survey')

        if represents_int(event_survey):
            self.event_survey = get_object_or_404(EventSurvey, pk=event_survey)
        else:
            return HttpResponse(status=400, content="Bad event_survey id.")

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # TODO: add a pre-check to validate if all lot ids are valid.

        data = dict(request.POST)
        lots = []
        for key, item in data.items():
            if 'lots' in key:
                lot_pk = key.replace('lots[', '').replace(']', '')
                status = item[0].replace('[', '').replace(']', '')
                status = status == 'true'
                lots.append({'lot': lot_pk, 'status': status})

        for item in lots:
            lot = Lot.objects.get(pk=item['lot'], event=self.event.pk)

            if item['status'] is True:
                lot.event_survey = self.event_survey
                lot.save()

            if item['status'] is False and \
                    lot.event_survey == self.event_survey:
                lot.event_survey = None
                lot.save()

        return HttpResponse(status=200)
