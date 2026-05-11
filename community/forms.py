from django import forms
from .models import Post, Comment, Profile # 🚨 Profile eklendi
from tracking.models import DependencyGoal # Hedef düzenleme için eklendi

# --- GÖNDERİ FORMU ---
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
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
                'class': 'form-select'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
        }

# --- YORUM FORMU ---
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

# --- 🚨 YENİ: PROFİL BİO FORMU ---
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        labels = {
            'bio': 'Hakkımda / Biyografi'
        }
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control rounded-4 bg-light border-0',
                'placeholder': 'Kendinden, hedeflerinden veya seni neyin motive ettiğinden bahset...',
                'rows': 4
            }),
        }

# --- 🚨 YENİ: HEDEF DÜZENLEME FORMU ---
# Edit_profile sayfasında hedef bilgilerini de güncellemek istersen bunu kullanırız
class GoalForm(forms.ModelModel):
    class Meta:
        model = DependencyGoal
        fields = ['initial_score'] # İhtiyaca göre alan ekleyebilirsin
        labels = {
            'initial_score': 'Başlangıç Puanı / Hedef'
        }
        widgets = {
            'initial_score': forms.NumberInput(attrs={
                'class': 'form-control rounded-pill bg-light border-0'
            }),
        }