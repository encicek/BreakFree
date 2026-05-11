from django.urls import path
from . import views

app_name = 'yonetim'

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    # 🚨 KULLANICI LİSTESİ İÇİN YENİ LİNK 🚨
    path('kullanicilar/', views.user_list, name='user_list'),
    path('kullanicilar/sil/<int:pk>/', views.user_delete, name='user_delete'),
    path('kullanicilar/ekle/', views.user_create, name='user_create'), 
    path('hedefler/', views.goal_list, name='goal_list'),
    path('topluluk/', views.post_list, name='post_list'),
    path('topluluk/sil/<int:pk>/', views.post_delete, name='post_delete'),
    path('basari-takibi/', views.success_tracking, name='success_tracking'),
]