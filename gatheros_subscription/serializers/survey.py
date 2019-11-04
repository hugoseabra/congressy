from typing import Any

from django.forms import model_to_dict
from rest_framework import serializers

from gatheros_subscription.models import EventSurvey, Subscription
from survey.models import Question, Option, Answer


class EventSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSurvey
        fields = [
            'pk',
            'event',
            'survey',
        ]

    def to_representation(self, instance: Any) -> Any:
        from django.forms import model_to_dict

        survey = instance.survey
        rep = {
            'pk': instance.pk,
        }

        rep.update(model_to_dict(survey))
        del rep['id']

        event = instance.event
        rep['event_data'] = {
            'pk': event.pk,
            'name': event.name,
            'slug': event.slug,
        }

        rep['num_questions'] = survey.questions.count()

        return rep


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.subscription_pk = None
        if 'subscription_pk' in kwargs:
            subscription_pk = kwargs.pop('subscription_pk')
            if subscription_pk:
                self.subscription_pk = subscription_pk
        super().__init__(*args, **kwargs)

    def get_answer(self, question: Question):
        if not self.subscription_pk:
            return None

        try:
            subscription = Subscription.objects.get(pk=self.subscription_pk)
        except Subscription.DoesNotExist:
            return None

        qs_exists = Question.objects.filter(
            survey__event__event_id=subscription.event_id
        )

        if qs_exists.exists() is False:
            return None

        person = subscription.person
        if hasattr(person, 'user') is True:
            user = person.user
            answers = Answer.objects.filter(
                question_id=question.pk,
                author__user_id=user.pk,
            ).order_by('created')

            if answers.count():
                return answers.first()

        answers = Answer.objects.filter(
            question_id=question.pk,
            author__subscription=subscription,
        ).order_by('created')

        if answers.count():
            return answers.last()

        return None

    def to_representation(self, instance: Any) -> Any:
        rep = super().to_representation(instance)

        from django.forms import model_to_dict

        survey = instance.survey
        rep['survey_data'] = model_to_dict(survey)

        rep['num_answers'] = instance.answers.count()

        event = survey.event.event
        rep['event_data'] = {
            'pk': event.pk,
            'name': event.name,
            'slug': event.slug,
        }

        has_options = instance.has_options
        rep['has_options'] = has_options

        if has_options is True:
            rep['options'] = list()

            for option in instance.options.all():
                rep['options'].append({
                    'pk': option.pk,
                    'text': option.name,
                    'value': option.value,
                })

        if self.subscription_pk:
            rep['answer'] = dict()

            answer = self.get_answer(instance)
            if answer:
                rep['answer'] = {
                    'pk': answer.pk,
                    'author': answer.author_id,
                    'author_data': model_to_dict(answer.author),
                    'human_display': answer.human_display,
                    'value': answer.value,
                }
                if answer.author.user_id:
                    user = answer.author.user
                    rep['answer']['author_data'].update({
                        'user_data': {
                            'pk': user.pk,
                            'fist_name': user.first_name,
                            'last_name': user.last_name,
                            'email': user.email,
                            'last_login': user.last_login,
                        }
                    })

        return rep


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

    def to_representation(self, instance: Any) -> Any:
        rep = super().to_representation(instance)

        question = instance.question
        survey = question.survey
        rep['survey_data'] = model_to_dict(survey)

        rep['question_data'] = model_to_dict(question)

        event = survey.event.event
        rep['event_data'] = {
            'pk': event.pk,
            'name': event.name,
            'slug': event.slug,
        }

        return rep


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

    def to_representation(self, instance: Any) -> Any:
        rep = super().to_representation(instance)

        author = instance.author
        rep['author_data'] = model_to_dict(author)
        rep['user_data'] = dict()

        if author.user_id:
            user = author.user
            rep['user_data'].update({
                'pk': user.pk,
                'fist_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login': user.last_login,
            })

        question = instance.question
        survey = question.survey
        rep['survey_data'] = model_to_dict(survey)

        rep['question_data'] = model_to_dict(question)

        event = survey.event.event
        rep['event_data'] = {
            'pk': event.pk,
            'name': event.name,
            'slug': event.slug,
        }

        return rep
