from django.views import generic
from gatheros_event.views.mixins import EventViewMixin
from survey.forms import NewComplexQuestionForm, NewSimpleQuestionForm, \
    QuestionModelForm
from django.shortcuts import render


class CreateSurveyView(EventViewMixin, generic.TemplateView):
    template_name = 'survey/create.html'

    def dispatch(self, request, *args, **kwargs):

        self.event = self.get_event()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['simple_form'] = NewSimpleQuestionForm(prefix='simple_form')
        context['complex_form'] = NewComplexQuestionForm(prefix='complex_form')

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            self.template_name = 'survey/fields.html'

        response = super().render_to_response(context, **response_kwargs)

        return response

    def post(self, request, *args, **kwargs):

        # instantiate all unique forms (using prefix) as unbound
        simple_form = NewSimpleQuestionForm(prefix='simple_form')
        complex_form = NewComplexQuestionForm(prefix='complex_form')

        # determine which form is submitting (based on hidden input called
        # 'action')
        if 'simple_form-type' in request.POST:
            form_type = 'simple'
        elif 'complex_form-type' in request.POST:
            form_type = 'complex'

        # bind to POST and process the correct form
        if form_type == 'simple':
            simple_form = NewSimpleQuestionForm(request.POST,
                                                prefix='simple_form')
            if simple_form.is_valid():
                question_model_form = QuestionModelForm(
                    data=simple_form.cleaned_data)
                if question_model_form.is_valid():
                    question_model_form.save()
                else:
                    """
                        TO BE CONTINUED: FORM VALIDATION AND INTEGRATION 
                        WITH MANAGER. MESSAGES AND ERRORS
                    """

                    render(request, self.template_name)
        elif form_type == 'complex':
            complex_form = NewComplexQuestionForm(request.POST,
                                                  prefix='complex_form')
            if complex_form.is_valid():
                complex_form.save()


        # prep context
        context = {
            'simple_form': simple_form,
            'complex_form': complex_form,
        }

        return render(request, self.template_name, context)
