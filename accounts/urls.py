from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login sayfası
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    # accounts/urls.py
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('register/', views.register, name='register'),

    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
]