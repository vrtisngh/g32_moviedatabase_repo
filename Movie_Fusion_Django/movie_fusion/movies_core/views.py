from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Genre, Director, Actor, UserProfile, MovieList, Watchlist, FavoriteMovie
from reviews.models import Review
from .forms import MovieForm, MovieSearchForm, UserRegisterForm,UserProfileForm,MovieListForm
from django.utils.text import slugify
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'There was a problem with your registration. Please check the form and try again.')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# movies_core/views.py
def home_view(request):
    # Get recent and top-rated movies
    recent_movies = Movie.objects.all().order_by('-release_date')[:20]
    
    # Get top-rated movies using the average_rating property
    all_movies = list(Movie.objects.all())
    # Sort by average_rating, handling None values
    top_rated_movies = sorted(
        [m for m in all_movies if m.average_rating is not None],
        key=lambda m: m.average_rating,
        reverse=True
    )[:4]
    
    # Get all genres for the genre section
    genres = Genre.objects.exclude(name__isnull=True).exclude(name='')
    genre_data = [
        {'name': genre.name, 'slug': slugify(genre.name)}
        for genre in genres
        if genre.name and slugify(genre.name)  # Ensure slug is non-empty
    ]
    # Get popular actors
    from django.db.models import Count
    actors = Actor.objects.annotate(num_movies=Count('movies')).order_by('-num_movies')
    
    # Get available years from the movie release dates
    years_queryset = Movie.objects.dates('release_date', 'year', order='DESC')
    years = [date.year for date in years_queryset]
    
    # Get popular directors
    directors = Director.objects.annotate(num_movies=Count('movies')).order_by('-num_movies')
    
    # Since there's no Platform model, we'll use streaming_url as a proxy
    # Create a list of unique streaming platforms from the streaming_url field
    all_streaming_urls = Movie.objects.exclude(streaming_url__isnull=True).values_list('streaming_url', flat=True)
    
    # Extract domain names from URLs to represent platforms
    import re
    from urllib.parse import urlparse
    
    platforms_set = set()
    for url in all_streaming_urls:
        if url:
            domain = urlparse(url).netloc
            # Extract the base domain (e.g., netflix.com from www.netflix.com)
            base_domain = re.sub(r'^www\.', '', domain)
            if base_domain:
                platforms_set.add(base_domain)
    
    # Convert to list of dicts for the template
    platforms = [{'name': p} for p in platforms_set][:8]
    
    context = {
        'recent_movies': recent_movies,
        'top_rated_movies': top_rated_movies,
        'genres': genres,
        'actors': actors,
        'years': years,
        'directors': directors,
        'platforms': platforms,
        'genres':genre_data,
    }
    return render(request, 'movies_core/home.html', context)

class MovieListView(ListView): #built-in generic viiew to list objects
    model = Movie
    template_name = 'movies_core/movie_list.html'
    context_object_name = 'movies' #giving the rendered var a name
    paginate_by = 12 #12 items per page
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = MovieSearchForm(self.request.GET)
        
        if form.is_valid():
            query = form.cleaned_data.get('query')
            genre = form.cleaned_data.get('genre')
            sort_by = form.cleaned_data.get('sort_by')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query)
                )
                if not queryset.exists() and query:
                    messages.info(self.request, f'No movies found for "{query}". Showing all movies instead.')
                    return Movie.objects.all().order_by('-release_date')
            
            if genre:
                queryset = queryset.filter(genres=genre)
                if not queryset.exists():
                    genre_name = Genre.objects.get(pk=genre).name
                    messages.info(self.request, f'No movies found in the "{genre_name}" genre. Showing all movies instead.')
                    return Movie.objects.all().order_by('-release_date')
            
            if sort_by:
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('-release_date')
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MovieSearchForm(self.request.GET)
        context['genres'] = Genre.objects.all()
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies_core/movie_detail.html'
    context_object_name = 'movie'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        
        # Get reviews for the movie
        reviews = Review.objects.filter(movie=movie).order_by('-created_at')
        context['reviews'] = reviews
        
        # Check if user has added movie to watchlist or favorites
        if self.request.user.is_authenticated:
            context['in_watchlist'] = Watchlist.objects.filter(user=self.request.user, movie=movie).exists()
            context['in_favorites'] = FavoriteMovie.objects.filter(user=self.request.user, movie=movie).exists()
            context['user_lists'] = MovieList.objects.filter(user=self.request.user)
            context['in_lists'] = MovieList.objects.filter(user=self.request.user, movies=movie)
            context['user_has_reviewed'] = Review.objects.filter(user=self.request.user, movie=movie).exists()
            
            # Get user's liked and disliked reviews
            context['user_liked_reviews'] = [review.id for review in reviews if self.request.user in review.likes.all()]
            context['user_disliked_reviews'] = [review.id for review in reviews if self.request.user in review.dislikes.all()]
            
            # Get user's liked and disliked replies
            # This creates a dictionary where keys are reply IDs and values are True
            user_liked_replies = {}
            user_disliked_replies = {}
            
            for review in reviews:
                for reply in review.replies.all():
                    if self.request.user in reply.likes.all():
                        user_liked_replies[reply.id] = True
                    if self.request.user in reply.dislikes.all():
                        user_disliked_replies[reply.id] = True
            
            context['user_liked_replies'] = user_liked_replies
            context['user_disliked_replies'] = user_disliked_replies
        
        return context

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to access this page.")
            return self.handle_no_permission()
        if not self.test_func():
            messages.error(request, "You don't have permission to access this page.")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class MovieCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movies_core/movie_form.html'
    success_url = reverse_lazy('movie_list') #generates urls from view names
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Movie '{self.object.title}' created successfully!")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "There was an error creating the movie. Please check the form and try again.")
        return super().form_invalid(form)

class MovieUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movies_core/movie_form.html'
    
    def get_success_url(self):
        return reverse_lazy('movie_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Movie '{self.object.title}' updated successfully!")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the movie. Please check the form and try again.")
        return super().form_invalid(form)

class MovieDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Movie
    template_name = 'movies_core/movie_confirm_delete.html'
    success_url = reverse_lazy('movie_list')
    
    def delete(self, request, *args, **kwargs):
        movie = self.get_object()
        title = movie.title
        messages.success(request, f"Movie '{title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        url = super().get_success_url()
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return url
    
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)

    def get_next_page(self):
        return reverse_lazy('home') #or whatever your home page is named.
    
def add_movie_to_list(request, movie_list_id):
    movie_list = get_object_or_404(MovieList, id=movie_list_id)
    if request.method == 'POST':
        movie_ids = request.POST.getlist('movies')  # Get a list of movie IDs from the POST request.
        for movie_id in movie_ids:
            movie = get_object_or_404(Movie, id=movie_id)
            movie_list.movies.add(movie)
        messages.success(request, "Movies added to list successfully.")
        return redirect('movie_list_detail', movie_list_id=movie_list_id)

    movies = Movie.objects.all()  # Or filter movies as needed.
    return render(request, 'add_movie_to_list.html', {'movie_list': movie_list, 'movies': movies})

# User Profile Views
@login_required
def user_profile(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user reviews, watchlist, favorites, and movie lists
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    watchlist = Watchlist.objects.filter(user=request.user).order_by('-added_at')
    favorites = FavoriteMovie.objects.filter(user=request.user).order_by('-added_at')
    movie_lists = MovieList.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'profile': profile,
        'reviews': reviews,
        'watchlist': watchlist,
        'favorites': favorites,
        'movie_lists': movie_lists,
    }
    
    return render(request, 'movies_core/profile/user_profile.html', context)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    genres = Genre.objects.all()  # Assuming Genre is your model for genres
    return render(request, 'movies_core/profile/edit_profile.html', {
        'form': form,
        'genres': genres,  # Include genres in the context
        'user': request.user,  # Make sure user context is available
    })

@login_required
def user_watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user).order_by('-added_at')
    return render(request, 'movies_core/profile/user_watchlist.html', {'watchlist': watchlist})

@login_required
def user_favorites(request):
    favorites = FavoriteMovie.objects.filter(user=request.user).order_by('-added_at')
    return render(request, 'movies_core/profile/user_favorites.html', {'favorites': favorites})

@login_required
def user_movie_lists(request):
    movie_lists = MovieList.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'movies_core/profile/user_movie_lists.html', {'movie_lists': movie_lists})

@login_required
def create_movie_list(request):
    if request.method == 'POST':
        form = MovieListForm(request.POST)
        if form.is_valid():
            movie_list = form.save(commit=False)
            movie_list.user = request.user
            movie_list.save()
            messages.success(request, f'Movie list "{movie_list.name}" has been created successfully!')
            return redirect('movie_list_detail', list_id=movie_list.id)
    else:
        form = MovieListForm()
    
    return render(request, 'movies_core/profile/movie_list_form.html', {'form': form, 'is_create': True})

@login_required
def movie_list_detail(request, list_id):
    movie_list = get_object_or_404(MovieList, id=list_id, user=request.user)
    return render(request, 'movies_core/profile/movie_list_detail.html', {'movie_list': movie_list})

@login_required
def edit_movie_list(request, list_id):
    movie_list = get_object_or_404(MovieList, id=list_id, user=request.user)
    
    if request.method == 'POST':
        form = MovieListForm(request.POST, instance=movie_list)
        if form.is_valid():
            form.save()
            messages.success(request, f'Movie list "{movie_list.name}" has been updated successfully!')
            return redirect('movie_list_detail', list_id=movie_list.id)
    else:
        form = MovieListForm(instance=movie_list)
    
    return render(request, 'movies_core/profile/movie_list_form.html', {'form': form, 'movie_list': movie_list, 'is_create': False})

@login_required
def delete_movie_list(request, list_id):
    movie_list = get_object_or_404(MovieList, id=list_id, user=request.user)
    
    if request.method == 'POST':
        movie_list_name = movie_list.name
        movie_list.delete()
        messages.success(request, f'Movie list "{movie_list_name}" has been deleted successfully!')
        return redirect('user_movie_lists')
    
    return render(request, 'movies_core/profile/delete_movie_list.html', {'movie_list': movie_list})

# AJAX actions for movies: ASYNCHRONOUS JS AND XML
#allows for updating part of page without reloading the entire page
@login_required
def toggle_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
    
    if not created:
        watchlist_item.delete()
        in_watchlist = False
        messages.success(request, f'"{movie.title}" has been removed from your watchlist.')
    else:
        in_watchlist = True
        messages.success(request, f'"{movie.title}" has been added to your watchlist.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'in_watchlist': in_watchlist})
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('movie_detail', args=[movie_id])))

@login_required
def toggle_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    favorite_item, created = FavoriteMovie.objects.get_or_create(user=request.user, movie=movie)
    
    if not created:
        favorite_item.delete()
        in_favorites = False
        messages.success(request, f'"{movie.title}" has been removed from your favorites.')
    else:
        in_favorites = True
        messages.success(request, f'"{movie.title}" has been added to your favorites.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'in_favorites': in_favorites})
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('movie_detail', args=[movie_id])))

@login_required
def add_to_list(request, movie_id, list_id):
    movie = get_object_or_404(Movie, id=movie_id)
    movie_list = get_object_or_404(MovieList, id=list_id, user=request.user)
    
    movie_list.movies.add(movie)
    movie_list.save()
    
    messages.success(request, f'"{movie.title}" has been added to "{movie_list.name}".')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('movie_detail', args=[movie_id])))

@login_required
def remove_from_list(request, movie_id, list_id):
    movie = get_object_or_404(Movie, id=movie_id)
    movie_list = get_object_or_404(MovieList, id=list_id, user=request.user)
    
    movie_list.movies.remove(movie)
    movie_list.save()
    
    messages.success(request, f'"{movie.title}" has been removed from "{movie_list.name}".')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('movie_list_detail', args=[list_id])))


# In your app's signals.py or models.py
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib import messages

@receiver(user_logged_out) #used to connect signal
def user_logged_out_message(sender, request, user, **kwargs):
    # Note: user can be None here if already logged out
    if user:
        messages.success(request, f"Goodbye, {user.username}! You have been logged out.")
    else:
        messages.success(request, "You have been logged out.")

from django.db.models import Q
from .models import Movie

def search_movies(request):
    query = request.GET.get('q', '') #1st para for the search item and 2nd for empty
    movies = Movie.objects.all()
#q is used to build complex queries with OR conditions , checking if any field contains the search term
    if query: # if string not empty
        try:
            year = int(query)
        except ValueError: #guves anything other than int value
            year = None

        q_filters = (
            Q(title__icontains=query) | #logical OR
            Q(actors__name__icontains=query) |
            Q(director__name__icontains=query) |
            Q(genres__name__icontains=query)
        )

        if year:
            q_filters |= Q(release_date__year=year)

        movies = movies.filter(q_filters).distinct()

    return render(request, 'movies_core/search_results.html', {'results': movies, 'query': query})


def about_us(request):
    return render(request, 'about.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def contact(request):
    # Basic view for now - you can add form handling logic later
    return render(request, 'contact.html')

