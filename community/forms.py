from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'addiction_type']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience...',
                'rows': 5
            }),
            'addiction_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment...',
                'rows': 3
            }),
        }