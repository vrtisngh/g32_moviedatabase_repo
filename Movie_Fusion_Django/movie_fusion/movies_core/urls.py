from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movies/add/', views.MovieCreateView.as_view(), name='movie_create'),
    path('movies/<int:pk>/edit/', views.MovieUpdateView.as_view(), name='movie_update'),
    path('movies/<int:pk>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),
    
    # Profile related URLs
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/movies/watchlist/', views.user_watchlist, name='user_watchlist'),
    path('profile/movies/favorites/', views.user_favorites, name='user_favorites'),
    path('profile/movies/lists/', views.user_movie_lists, name='user_movie_lists'),
    path('profile/movies/lists/create/', views.create_movie_list, name='create_movie_list'),
    path('profile/movies/lists/<int:list_id>/', views.movie_list_detail, name='movie_list_detail'),
    path('profile/movies/lists/<int:list_id>/edit/', views.edit_movie_list, name='edit_movie_list'),
    path('profile/movies/lists/<int:list_id>/delete/', views.delete_movie_list, name='delete_movie_list'),
    
    # AJAX actions for movies
    path('movies/<int:movie_id>/watchlist/toggle/', views.toggle_watchlist, name='toggle_watchlist'),
    path('movies/<int:movie_id>/favorite/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('movies/<int:movie_id>/add-to-list/<int:list_id>/', views.add_to_list, name='add_to_list'),
    path('movies/<int:movie_id>/remove-from-list/<int:list_id>/', views.remove_from_list, name='remove_from_list'),
    
    path('search/', views.search_movies, name='search_movies'),
    path('about/', views.about_us, name='about'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact/', views.contact, name='contact'),

    path('filter/actor/<str:actor_name>/', api_views.filter_by_actor, name='filter_by_actor'),
    path('filter/year/<int:year>/', api_views.filter_by_year, name='filter_by_year'),
    path('filter/platform/<str:platform_name>/', api_views.filter_by_platform, name='filter_by_platform'),



    # CURRENTLY NOT IN USE


    path('search/', api_views.advanced_search, name='advanced_search'),
    
    # Sorting routes
    path('sort/actors/', api_views.sort_by_actors, name='sort_by_actors'),
    path('sort/genres/', api_views.sort_by_genres, name='sort_by_genres'),
    path('sort/years/', api_views.sort_by_years, name='sort_by_years'),
    
    # Recommendations
    path('recommendations/<int:movie_id>/', api_views.get_recommendations, name='get_recommendations'),
]