from rest_framework import serializers

from apps.core.models import City, Genre, Language


class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for genre model

    Structure:
    {
        "id": int,
        "name": string
    }
    """

    class Meta:
        model = Genre
        fields = ("id", "name")


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for language model

    Structure:
    {
        "id": int,
        "name": string
    }
    """

    class Meta:
        model = Language
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for city model

    Structure:
    {
        "id": int,
        "name": string
    }
    """

    class Meta:
        model = City
        fields = ("id", "name")
