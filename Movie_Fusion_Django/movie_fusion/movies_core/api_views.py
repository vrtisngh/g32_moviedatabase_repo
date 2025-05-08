import requests # type: ignore
from django.shortcuts import render # type: ignore
from django.http import JsonResponse # type: ignore
from django.views.decorators.http import require_http_methods # type: ignore
from django.shortcuts import get_object_or_404 # type: ignore
from urllib.parse import urlparse
import re
from .models import Movie, Genre, Actor, Director

# Configure the Flask API base URL
FLASK_API_BASE = "http://127.0.0.1:5001/api"

@require_http_methods(["GET"])
def filter_by_genre(request, genre_name):
    try:
        cleaned_genre_name = genre_name.replace("-", " ").title()

        response = requests.get(f'{FLASK_API_BASE}/genre/{genre_name}')
        response.raise_for_status()

        genre = get_object_or_404(Genre, name__iexact=cleaned_genre_name)

        movies = Movie.objects.filter(genres=genre)

        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'genre_name': cleaned_genre_name
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)
    except Genre.DoesNotExist:
        return JsonResponse({
            'error': 'Genre not found'
        }, status=404)


@require_http_methods(["GET"])
def filter_by_actor(request, actor_name):
    try:
        actor_name_cleaned = actor_name.replace("-", " ")
        response = requests.get(f'{FLASK_API_BASE}/actor/{actor_name}')
        response.raise_for_status()
        actor = get_object_or_404(Actor, name__iexact=actor_name_cleaned)
        movies = Movie.objects.filter(actors=actor)
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'actor_name': actor_name_cleaned,
            'actor_image': actor.image if actor and actor.image else '',
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def filter_by_director(request, director_name):
    try:
        response = requests.get(f'{FLASK_API_BASE}/director/{director_name}')
        response.raise_for_status()
        director = get_object_or_404(Director, name__iexact=director_name)
        movies = Movie.objects.filter(director=director)      
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'director_name': director_name
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def filter_by_year(request, year):
    try:
        response = requests.get(f'{FLASK_API_BASE}/year/{year}')
        response.raise_for_status()
        import datetime
        start_date = datetime.date(int(year), 1, 1)
        end_date = datetime.date(int(year), 12, 31)
        movies = Movie.objects.filter(
            release_date__gte=start_date,
            release_date__lte=end_date
        )
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'year': year
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def filter_by_platform(request, platform_name):
    try:
        response = requests.get(f'{FLASK_API_BASE}/platform/{platform_name}')
        response.raise_for_status()
        # Since we don't have a separate platform model, we'll use streaming_url
        # Filter movies where the streaming_url contains the platform name
        movies = Movie.objects.filter(streaming_url__icontains=platform_name)
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'platform_name': platform_name
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def sort_by_actors(request):
    try:
        response = requests.get(f'{FLASK_API_BASE}/sort_by_actors')
        response.raise_for_status()
        movies = Movie.objects.all().order_by('actors__name')
        
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'sort_type': 'actors'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def sort_by_genres(request):
    try:
        # Call Flask API for sorting by genres
        response = requests.get(f'{FLASK_API_BASE}/sort_by_genres')
        response.raise_for_status()
        
        # Get all movies and sort by genres (alphabetically)
        movies = Movie.objects.all().order_by('genres__name')
        
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'sort_type': 'genres'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def sort_by_years(request):
    try:
        response = requests.get(f'{FLASK_API_BASE}/sort_by_years')
        response.raise_for_status()
        movies = Movie.objects.all().order_by('-release_date')
        
        return render(request, 'movies_core/api_movie_filter.html', {
            'movies': movies,
            'sort_type': 'years'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def advanced_search(request):
    try:
        genre = request.GET.get('genre')
        actor = request.GET.get('actor')
        director = request.GET.get('director')
        year = request.GET.get('year')
        platform = request.GET.get('platform')
        query = request.GET.get('query')
        movies = Movie.objects.all()
        
        # Apply filters if provided
        if genre:
            movies = movies.filter(genres__name__iexact=genre)
        
        if actor:
            movies = movies.filter(actors__name__icontains=actor)
            
        if director:
            movies = movies.filter(director__name__icontains=director)
        
        if year:
            import datetime
            start_date = datetime.date(int(year), 1, 1)
            end_date = datetime.date(int(year), 12, 31)
            movies = movies.filter(release_date__gte=start_date, release_date__lte=end_date)
        
        if platform:
            # Filter by streaming_url containing the platform name
            movies = movies.filter(streaming_url__icontains=platform)
        
        if query:
            # Search in title and description
            from django.db.models import Q # type: ignore
            movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
        # Call Flask API for integrated filtering
        filter_params = {k: v for k, v in request.GET.items() if v}
        response = requests.get(f'{FLASK_API_BASE}/search', params=filter_params)
        response.raise_for_status()
        
        # Context for the template
        context = {
            'movies': movies,
            'search_params': {
                'genre': genre,
                'actor': actor,
                'director': director,
                'year': year,
                'platform': platform,
                'query': query
            }
        }
        
        return render(request, 'movies_core/api_movie_filter.html', context)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Flask API not available',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_recommendations(request, movie_id):
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        response = requests.get(f'{FLASK_API_BASE}/recommendations/{movie_id}')
        response.raise_for_status()
        data = response.json()
        recommended_ids = data.get('recommended_ids', [])
        recommended_movies = Movie.objects.filter(id__in=recommended_ids)
        # If Flask API doesn't return recommendations or IDs don't match, 
        # fall back to a simple genre-based recommendation
        if not recommended_movies.exists():
            # Get movies with the same genres
            genres = movie.genres.all()
            recommended_movies = Movie.objects.filter(genres__in=genres).exclude(id=movie_id).distinct()[:5]
            # If still no recommendations, include movies by the same director
            if not recommended_movies.exists() and movie.director:
                recommended_movies = Movie.objects.filter(director=movie.director).exclude(id=movie_id)[:5]
        
        return render(request, 'movies_core/api_movie_recommendations.html', {
            'movie': movie,
            'recommended_movies': recommended_movies
        })
    except requests.exceptions.RequestException as e:
        # Fall back to simple recommendations if API fails
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Try to get recommendations based on genres
        genres = movie.genres.all()
        recommended_movies = Movie.objects.filter(genres__in=genres).exclude(id=movie_id).distinct()[:5]
        
        # If no recommendations found by genre, try by director
        if not recommended_movies.exists() and movie.director:
            recommended_movies = Movie.objects.filter(director=movie.director).exclude(id=movie_id)[:5]
        
        return render(request, 'movies_core/api_movie_recommendations.html', {
            'movie': movie,
            'recommended_movies': recommended_movies,
            'api_error': str(e)
        })