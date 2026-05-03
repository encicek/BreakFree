from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # 🚨 DÜZENLEME: 'is_anonymous' alanı listeye eklendi
        fields = ['title', 'content', 'addiction_type', 'is_anonymous']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Bugünü de başarıyla tamamladım!'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Neler hissettiğini veya tecrübelerini buraya yazabilirsin...',
                'rows': 5
            }),
            'addiction_type': forms.Select(attrs={
                'class': 'form-select' # Bootstrap 5 uyumu için form-control yerine form-select
            }),
            # 🚨 DÜZENLEME: Anonimlik switch'i için checkbox widget'ı
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Bir destek mesajı veya yorum yaz...',
                'rows': 3
            }),
        }