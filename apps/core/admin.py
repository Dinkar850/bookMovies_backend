from django.contrib import admin

from .models import City, Genre, Language

admin.site.register(Language)
admin.site.register(City)
admin.site.register(Genre)
