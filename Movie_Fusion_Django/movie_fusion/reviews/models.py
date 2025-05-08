from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from movies_core.models import Movie

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='review_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='review_dislikes', blank=True)

    @property
    def like_count(self):
        return self.likes.count()
        
    @property
    def dislike_count(self):
        return self.dislikes.count()
    class Meta:
        unique_together = ('movie', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} review for {self.movie.title}'


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='reply_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='reply_dislikes', blank=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"Reply to {self.review.id} by {self.user.username}"