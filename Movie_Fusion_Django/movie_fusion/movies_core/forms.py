from django import forms
from .models import Movie, Genre, Director, Actor, UserProfile, MovieList
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MovieForm(forms.ModelForm):
    class Meta: #special inner class to configure forms behaviour
        model = Movie
        fields = ['title', 'release_date', 'description', 'poster', 'genres', 'director', 'actors', 'duration','streaming_url']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'streaming_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }
        

class MovieSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Movie name',  # ✅ Change placeholder here
            'class': 'form-control'
        })
    )
    genre = forms.ModelChoiceField(
        required=False,
        queryset=Genre.objects.all(),
        empty_label="All Genres",
        label='Genre'
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('title', 'Title (A-Z)'),
            ('-title', 'Title (Z-A)'),
            ('release_date', 'Release Date (Oldest)'),
            ('-release_date', 'Release Date (Newest)'),
        ],
        label='Sort by'
    )


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'favorite_genres']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
        }

class MovieListForm(forms.ModelForm):
    class Meta:
        model = MovieList
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your movie list...'}),
        }
