
from rest_framework import serializers
from .models import Work, Author


class WorkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Work
        fields = (
            'modality',
            'area_category',
            'title',
            'summary',
            'keywords',
            'article_file',
            'banner_file'
        )


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = (
            'work',
            'user',
            'name',
        )


