from django.urls import path
from . import views


urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/support/', views.support_post, name='support_post'),
]