from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Review,ReviewReply
from .forms import ReviewForm
from movies_core.models import Movie

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    # Check if user already reviewed this movie
    existing_review = Review.objects.filter(movie=movie, user=request.user).first()
    if existing_review:
        messages.warning(request, "You have already reviewed this movie. You can edit your review instead.")
        return redirect('edit_review', review_id=existing_review.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            messages.success(request, f"Your review for '{movie.title}' has been submitted!")
            return redirect('movie_detail', pk=movie.id)
        else:
            messages.error(request, "There was an error with your review. Please check the form and try again.")
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'movie': movie,
        'action': 'Add'
    })

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, f"Your review for '{review.movie.title}' has been updated!")
            return redirect('movie_detail', pk=review.movie.id)
        else:
            messages.error(request, "There was an error updating your review. Please check the form and try again.")
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'movie': review.movie,
        'action': 'Edit'
    })

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    movie_id = review.movie.id
    movie_title = review.movie.title
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, f"Your review for '{movie_title}' has been deleted.")
        return redirect('movie_detail', pk=movie_id)
    
    return render(request, 'reviews/review_confirm_delete.html', {
        'review': review
    })

def user_reviews(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to view your reviews.")
        return redirect('login')
    
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    if not reviews.exists():
        messages.info(request, "You haven't written any reviews yet. Find a movie you like and share your thoughts!")
    
    return render(request, 'reviews/user_reviews.html', {
        'reviews': reviews
    })

@login_required
def review_like(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # If user already disliked this review, remove the dislike
    if request.user in review.dislikes.all():
        review.dislikes.remove(request.user)
    
    # Toggle like (add if not liked, remove if already liked)
    if request.user in review.likes.all():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)
    
    return redirect('movie_detail', pk=review.movie.id)

@login_required
def review_dislike(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # If user already liked this review, remove the like
    if request.user in review.likes.all():
        review.likes.remove(request.user)
    
    # Toggle dislike
    if request.user in review.dislikes.all():
        review.dislikes.remove(request.user)
    else:
        review.dislikes.add(request.user)
    
    return redirect('movie_detail', pk=review.movie.id)

@login_required
def add_reply(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment')
        if comment:
            ReviewReply.objects.create(
                review=review,
                user=request.user,
                comment=comment
            )
    
    return redirect('movie_detail', pk=review.movie.id)

@login_required
def edit_reply(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)
    
    # Only allow the reply author to edit
    if reply.user != request.user:
        messages.error(request, "You don't have permission to edit this reply.")
        return redirect('movie_detail', pk=reply.review.movie.id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment')
        if comment:
            reply.comment = comment
            reply.save()
            return redirect('movie_detail', pk=reply.review.movie.id)
    
    context = {
        'reply': reply,
        'movie': reply.review.movie
    }
    return render(request, 'edit_reply.html', context)

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)
    movie_id = reply.review.movie.id
    
    # Only allow the reply author to delete
    if reply.user != request.user:
        messages.error(request, "You don't have permission to delete this reply.")
        return redirect('movie_detail', pk=movie_id)
    
    if request.method == 'POST':
        reply.delete()
        messages.success(request, "Reply deleted successfully.")
        return redirect('movie_detail', pk=movie_id)
    
    context = {
        'reply': reply,
        'movie': reply.review.movie
    }
    return render(request, 'delete_reply.html', context)

@login_required
def reply_like(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)
    
    # If user already disliked this reply, remove the dislike
    if request.user in reply.dislikes.all():
        reply.dislikes.remove(request.user)
    
    # Toggle like
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
    else:
        reply.likes.add(request.user)
    
    return redirect('movie_detail', pk=reply.review.movie.id)

@login_required
def reply_dislike(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)
    
    # If user already liked this reply, remove the like
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
    
    # Toggle dislike
    if request.user in reply.dislikes.all():
        reply.dislikes.remove(request.user)
    else:
        reply.dislikes.add(request.user)
    
    return redirect('movie_detail', pk=reply.review.movie.id)

