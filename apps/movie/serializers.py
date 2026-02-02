from rest_framework import serializers

from .models import Movie


class MovieNameSerializer(serializers.ModelSerializer):
    """Serializer for only showing the `id` and `name`` of the movie"""

    class Meta:
        model = Movie
        fields = ["id", "name"]


class MovieListSerializer(MovieNameSerializer):
    """
    Serializer for movies in list:
    - returns genre and language as strings (defined in def(__str__))
    """

    genres = serializers.StringRelatedField(many=True, read_only=True)
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(MovieNameSerializer.Meta):
        fields = MovieNameSerializer.Meta.fields + [
            "slug",
            "genres",
            "languages",
            "cover_image",
            "release_date",
        ]


class MovieDetailsSerializer(MovieListSerializer):
    """
    Serializer for movie details:
    - returns all details as in `MovieListSerializer`
    - additonally include description
    """

    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + ["description"]
