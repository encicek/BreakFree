from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # Ana Sayfa ve Gönderi İşlemleri
    path('', views.community_home, name='community_home'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/support/', views.support_post, name='support_post'),
    
    # Sosyal İşlemler
    path('find-friends/', views.user_list, name='user_list'),
    path('toggle-friend/<int:user_id>/', views.toggle_friend, name='toggle_friend'),

    # --- PROFİL VE DÜZENLEME (SIRALAMA KRİTİK) ---
    
    # 1. Belirli bir hedefi düzenleme yolu (ID ile)
    path('profile/edit/<int:goal_id>/', views.edit_profile, name='edit_profile'),
    
    # 2. Genel profil görüntüleme yolu (Username ile)
    # Bu en altta kalmalı ki 'edit' kelimesini kullanıcı adı sanmasın.
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]