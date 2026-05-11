from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# 🚨 LOGIN_URL KISMINI GİZLİ ADMİN OLARAK DEĞİŞTİRDİK 🚨
@staff_member_required(login_url='/gizli-admin/login/') 
def dashboard(request):
    return render(request, 'yonetim/dashboard.html')