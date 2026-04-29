from django.urls import path
from . import views

app_name = 'tracking' # İleride link verirken karışmaması için isimlendiriyoruz

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
path('yeni-hedef/', views.create_goal, name='create_goal'),
]