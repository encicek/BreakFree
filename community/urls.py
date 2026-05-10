from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # --- ANA SAYFA VE GÖNDERİ İŞLEMLERİ ---
    path('', views.community_home, name='community_home'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/support/', views.support_post, name='support_post'),
    path('post/<int:post_id>/report/', views.report_post, name='report_post'),

    # --- BİLDİRİMLER (Profilin Üstünde Olmalı) ---
    path('notifications/', views.notifications, name='notifications'),

    # --- SOSYAL İŞLEMLER ---
    path('find-friends/', views.user_list, name='user_list'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_request'),
    path('accept-request/<int:notification_id>/', views.accept_friend_request, name='accept_request'),
    path('reject-request/<int:notification_id>/', views.reject_friend_request, name='reject_request'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),

    # --- PROFİL VE DÜZENLEME ---
    # Düzenleme (ID bazlı) profil görüntülemeden (String bazlı) önce gelmeli
    path('profile/edit/<int:goal_id>/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]