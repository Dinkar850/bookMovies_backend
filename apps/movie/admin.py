from django.contrib import admin

from .models import Movie


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
    search_fields = ("name",)
    filter_horizontal = ("genre", "language")
