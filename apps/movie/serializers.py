from rest_framework import serializers

from .models import Movie


class MovieListSerializer(serializers.ModelSerializer):
    """
    Serializer for movies in list:
    - returns genre and language as strings (defined in def(__str__))
    """

    genre = serializers.StringRelatedField(many=True)
    language = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        fields = ["id", "name", "genre", "language", "cover_image"]


class MovieDetailsSerializer(MovieListSerializer):
    """
    Serializer for movie details:
    - returns all details as in `MovieListSerializer`
    - additonally include description and release_date
    """

    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + ["description", "release_date"]
