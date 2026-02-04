from django.contrib import admin

from apps.movie.models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "duration",
        "release_date",
        "cover_image",
    )
    list_filter = ("languages", "genres")
    search_fields = ("name",)
    filter_horizontal = ("genres", "languages")
