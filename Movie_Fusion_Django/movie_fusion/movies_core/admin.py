from django.contrib import admin
from .models import Movie, Genre, Director, Actor

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'director')
    list_filter = ('genres', 'release_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres', 'actors')
    date_hierarchy = 'release_date'
