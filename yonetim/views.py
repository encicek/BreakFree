from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from tracking.models import DependencyGoal
from community.models import Post

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

@staff_member_required(login_url='/gizli-admin/login/') 
def user_list(request):
    query = request.GET.get('q', '') 
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).prefetch_related('earned_badges__badge', 'goals').order_by('-date_joined')
    else:
        users = User.objects.all().prefetch_related('earned_badges__badge', 'goals').order_by('-date_joined')

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'yonetim/user_list.html', context)

# 🚨 YENİ: KULLANICI SİLME FONKSİYONU
@staff_member_required(login_url='/gizli-admin/login/')
def user_delete(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Kendini silmeyi engelleme
    if user_to_delete == request.user:
        messages.error(request, "Kendi yönetici hesabınızı silemezsiniz!")
    else:
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"{username} isimli kullanıcı başarıyla silindi.")
        
    return redirect('yonetim:user_list')

# 🚨 YENİ: KULLANICI EKLEME FONKSİYONU
@staff_member_required(login_url='/gizli-admin/login/')
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten sistemde kayıtlı.")
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, f"{username} kullanıcısı başarıyla oluşturuldu.")
            
    return redirect('yonetim:user_list')