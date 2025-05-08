from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']  # Include whichever fields you want in the form

    def clean(self):
        cleaned_data = super().clean() #uses parent class's clean method(super())
        rating = cleaned_data.get('rating')
        comment = cleaned_data.get('comment')

        if not rating and not comment:
            raise forms.ValidationError("Please provide at least a rating or a comment.")

        return cleaned_data
