from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('find-friends/', views.user_list, name='user_list'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('toggle-friend/<int:user_id>/', views.toggle_friend, name='toggle_friend'),
    # EKSİK OLAN SATIR BURASIYDI:
    path('post/<int:post_id>/support/', views.support_post, name='support_post'),
]