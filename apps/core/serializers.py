from rest_framework import serializers

from .models import City, Genre, Language


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre"""

    class Meta:
        model = Genre
        fields = ["id", "name"]


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for language"""

    class Meta:
        model = Language
        fields = ["id", "name"]


class CitySerializer(serializers.ModelSerializer):
    """Serializer for city"""

    class Meta:
        model = City
        fields = ["id", "name"]
