# yonetim/urls.py
from django.urls import path
from . import views

app_name = 'yonetim'

urlpatterns = [
    # /yonetim/ adresine girilince dashboard fonksiyonu çalışacak
    path('', views.dashboard, name='dashboard'), 
]