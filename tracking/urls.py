from django.urls import path
from . import views

app_name = 'tracking' 

urlpatterns = [
    # Boş string yerine 'dashboard/' ekledik
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('yeni-hedef/', views.create_goal, name='create_goal'),
    path('anket/', views.survey_view, name='survey'),
    
    # Eğer ana 'tracking/' adresine girince de dashboard açılsın istersen bunu da bırakabilirsin:
    path('', views.dashboard, name='dashboard_alt'),
]