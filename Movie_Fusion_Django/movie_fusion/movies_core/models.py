from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Director(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Actor(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.URLField(null=True, blank=True)
    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    description = models.TextField()
    poster = models.URLField(max_length=500, blank=True, null=True) 
    genres = models.ManyToManyField(Genre, related_name='movies')
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, related_name='movies') #   ONE MOVIE HAS ONE DIRECTOR
    actors = models.ManyToManyField(Actor, related_name='movies')
    duration = models.IntegerField(help_text="Duration in minutes")
    streaming_url = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'pk': self.pk})
        
    @property
    #for it to behave like a read-only property
    def average_rating(self):
        ratings = [review.rating for review in self.reviews.all() if review.rating is not None]
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
            'description': self.description,
            'poster': self.poster,
            'genres': [genre.name for genre in self.genres.all()],
            'director': self.director.name if self.director else None,
            'actors': [actor.name for actor in self.actors.all()],
            'duration': self.duration,
            'streaming_url': self.streaming_url,
            'average_rating': self.average_rating,
        }

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.png')
    bio = models.TextField(blank=True)
    favorite_genres = models.ManyToManyField(Genre, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class MovieList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField(Movie, related_name='in_lists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
    
    def __str__(self):
        return f"{self.movie.title} in {self.user.username}'s watchlist"

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
    
    def __str__(self):
        return f"{self.movie.title} favorited by {self.user.username}"
    

#for my login message ex: welcome diksha
# In your models.py or a separate signals.py file
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages

@receiver(user_logged_in)
def user_logged_in_message(sender, request, user, **kwargs):
    messages.success(request, f'Welcome back, {user.username}!')