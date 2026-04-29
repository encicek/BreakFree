from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login olunca doğrudan senin seçim butonlarına (/tracking/) gitmesi sağlandı
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='/tracking/'), name='login'),
    
    # Logout olunca tekrar login sayfasına yönlendirir
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('register/', views.register, name='register'),
]