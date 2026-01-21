from rest_framework import serializers

from apps.slot import serializers as SlotSerializers

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
        fields = ["id", "name", "genre", "language", "cover_image", "release_date"]


class MovieDetailsSerializer(MovieListSerializer):
    """
    Serializer for movie details with slots of that:
    - returns all details as in `MovieListSerializer`
    - adds description and slots information fetched by `MovieDetailsView` in attribute `active_slots`
    """

    slots = SlotSerializers.SlotListSerializer(
        source="active_slots", many=True, read_only=True
    )

    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + ["description", "slots"]
