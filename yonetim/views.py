from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from tracking.models import DependencyGoal
from community.models import Post
from django.db.models import Q # 🚨 ARAMA (FİLTRELEME) İÇİN GEREKLİ

@staff_member_required(login_url='/gizli-admin/login/') 
def dashboard(request):
    total_users = User.objects.count()
    total_goals = DependencyGoal.objects.count()
    total_posts = Post.objects.count()

    context = {
        'total_users': total_users,
        'total_goals': total_goals,
        'total_posts': total_posts,
    }
    return render(request, 'yonetim/dashboard.html', context)

# 🚨 YENİ FONKSİYON: KULLANICI LİSTESİ VE ARAMA 🚨
@staff_member_required(login_url='/gizli-admin/login/') 
def user_list(request):
    # Arama kutusuna bir şey yazılmış mı diye bakıyoruz
    query = request.GET.get('q', '') 
    
    if query:
        # Eğer bir şey yazıldıysa, kullanıcı adı veya e-posta içinde bunu ara
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).order_by('-date_joined') # En son kayıt olan en üstte
    else:
        # Arama yapılmadıysa herkesi getir
        users = User.objects.all().order_by('-date_joined')

    context = {
        'users': users,
        'query': query, # Arama kutusunda yazılan silinmesin diye geri gönderiyoruz
    }
    return render(request, 'yonetim/user_list.html', context)