
from rest_framework import serializers
from .models import Work, Author, AreaCategory, WorkConfig


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Author
        fields = ('name', 'work', 'user')


class AreaCategorySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = AreaCategory
        fields = ('name', 'event')


class WorkConfigSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = WorkConfig
        fields = (
            'date_start',
            'date_end',
            'presenting_type',
            'event',
        )


class WorkSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Work
        fields = (
            'subscription',
            'modality',
            'area_category',
            'title',
            'summary',
            'keywords',
            'article_file',
            'banner_file',
            'published',
        )


