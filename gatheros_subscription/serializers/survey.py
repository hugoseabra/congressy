from typing import Any

from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from gatheros_subscription.models import EventSurvey, Subscription
from survey.models import Question, Option, Answer, Author


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
        rep['event'] = event.pk
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
                    'subscription': self.subscription_pk
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
    subscription = serializers.UUIDField(required=True, write_only=True)

    class Meta:
        model = Answer
        exclude = ('author', 'human_display')

    def validate_subscription(self, validated_value):
        try:
            sub = Subscription.objects.get(pk=validated_value)
        except Subscription.DoesNotExist:
            raise ValidationError('Subscription is invalid.')

        return sub

    def validate(self, attrs):
        attrs = super().validate(attrs)

        subscription = attrs.get('subscription')
        person = subscription.person
        question = attrs.get('question')

        user = None
        author = None

        if person.user_id:
            user = person.user
            authors = user.authors.filter(survey_id=question.survey_id)
            if authors.count():
                author = authors.last()

        if not author:
            author, _ = Author.objects.get_or_create(
                name=person.name,
                survey=question.survey,
                user=user,
            )

        subscription.author = author
        attrs['author'] = author

        answers = Answer.objects.filter(
            author=author,
            question=question,
        )

        if answers.count():
            self.instance = answers.last()
            self.partial = True

        return attrs

    def to_representation(self, instance: Any) -> Any:
        rep = super().to_representation(instance)

        author = instance.author
        rep['author_data'] = model_to_dict(author)
        rep['user_data'] = dict()

        sub = None
        if hasattr(author, 'subscription'):
            sub = author.subscription

        if author.user_id:
            user = author.user

            if not sub and user.authors.count():
                sub = user.authors.last()

            rep['user_data'].update({
                'pk': user.pk,
                'fist_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'last_login': user.last_login,
            })

        rep['subscription'] = sub.pk if sub else None

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

    def save(self, **kwargs):
        subscription = self.validated_data.pop('subscription')
        instance = super().save(**kwargs)
        subscription.save()
        return instance
