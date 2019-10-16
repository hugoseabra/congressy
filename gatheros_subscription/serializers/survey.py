from typing import Any

from rest_framework import serializers

from gatheros_subscription.models import EventSurvey
from survey.models import Question


class EventSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSurvey
        fields = [
            'pk',
            'event',
            'survey',
        ]

    def to_representation(self, instance: Any) -> Any:
        rep = super().to_representation(instance)

        from django.forms import model_to_dict

        survey = instance.survey
        rep['survey_data'] = model_to_dict(survey)

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

        return rep
