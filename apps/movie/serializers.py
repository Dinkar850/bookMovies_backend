from rest_framework import serializers

from apps.movie.models import Movie


class MovieNameSerializer(serializers.ModelSerializer):
    """
    Serializer for basic movie identity

    Structure:
    {
        "id": int,
        "name": string
    }
    """

    class Meta:
        model = Movie
        fields = ("id", "name")


class MovieListSerializer(MovieNameSerializer):
    """
    Serializer for movie list view

    Structure:
    {
        "id": int,
        "name": string,
        "slug": string,
        "genres": [string],
        "languages": [string],
        "cover_image": string,
        "release_date": date
    }

    Notes:
        - Genres returned as string using __str__
        - Languages returned as string using __str__
    """

    genres = serializers.StringRelatedField(many=True, read_only=True)
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(MovieNameSerializer.Meta):
        fields = MovieNameSerializer.Meta.fields + (
            "slug",
            "genres",
            "languages",
            "cover_image",
            "release_date",
        )


class MovieDetailsSerializer(MovieListSerializer):
    """
    Serializer for movie details

    Structure:
    {
        "id": int,
        "name": string,
        "slug": string,
        "genres": [string],
        "languages": [string],
        "cover_image": string,
        "release_date": date,
        "description": string
    }
    """

    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + ("description",)
