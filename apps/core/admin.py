from django.contrib import admin

from apps.core.models import City, Genre, Language

admin.site.register(Language)
admin.site.register(City)
admin.site.register(Genre)
