"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView # Ana sayfa yönlendirmesi için ekledik

# Admin Paneli Özelleştirmeleri
admin.site.site_header = "BreakFree Yönetim Paneli"
admin.site.site_title = "BreakFree Admin"
admin.site.index_title = "Sistem Yönetimine Hoş Geldiniz"

urlpatterns = [
    # Boş yolu (ana sayfayı) doğrudan login'e veya tracking'e yönlendiriyoruz
    # Bu satır Render'daki o sarı 404 sayfasını engelleyecek:
    path('', RedirectView.as_view(url='login/', permanent=True)), 

    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='/tracking/'), name='login'),
    path('tracking/', include('tracking.urls')),
    path('community/', include(('community.urls', 'community'), namespace='community')),
    path('accounts/', include('accounts.urls')),
]