
from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:movie_id>/', views.add_review, name='add_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('my-reviews/', views.user_reviews, name='user_reviews'),
    path('review/<int:review_id>/like/', views.review_like, name='review_like'),
    path('review/<int:review_id>/dislike/', views.review_dislike, name='review_dislike'),
    path('review/<int:review_id>/reply/', views.add_reply, name='add_reply'),
    path('reply/<int:reply_id>/edit/', views.edit_reply, name='edit_reply'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('reply/<int:reply_id>/like/', views.reply_like, name='reply_like'),
    path('reply/<int:reply_id>/dislike/', views.reply_dislike, name='reply_dislike'),
]
