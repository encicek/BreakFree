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
path('send-request/<int:user_id>/', views.send_friend_request, name='send_request'),path('accept-request/<int:notification_id>/', views.accept_friend_request, name='accept_request'),
path('reject-request/<int:notification_id>/', views.reject_friend_request, name='reject_request'),

    # --- PROFİL VE DÜZENLEME (SIRALAMA KRİTİK) ---
    
    # 1. Belirli bir hedefi düzenleme yolu (ID ile)
    path('profile/edit/<int:goal_id>/', views.edit_profile, name='edit_profile'),
    
    # 2. Genel profil görüntüleme yolu (Username ile)
    # Bu en altta kalmalı ki 'edit' kelimesini kullanıcı adı sanmasın.
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('post/<int:post_id>/report/', views.report_post, name='report_post'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    ]