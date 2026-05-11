from django.urls import path
from . import views

app_name = 'yonetim'

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    # 🚨 KULLANICI LİSTESİ İÇİN YENİ LİNK 🚨
    path('kullanicilar/', views.user_list, name='user_list'), 
]