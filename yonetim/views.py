# yonetim/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/accounts/login/') # Yetkisi olmayan login'e atılır
def dashboard(request):
    # İleride buraya veritabanından kullanıcı sayılarını vs. çekeceğiz
    return render(request, 'yonetim/dashboard.html')