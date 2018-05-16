
from rest_framework import serializers
from .models import Work, Author


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Author
        fields = ('name', 'user')


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
        )


