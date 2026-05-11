from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from tracking.models import DependencyGoal
from community.models import Post
import json # Grafik verilerini JSON formatına çevirmek için

# --- 1. ANA PANEL (DASHBOARD) ---
@staff_member_required(login_url='/gizli-admin/login/') 
def dashboard(request):
    # Temel Sayılar
    total_users = User.objects.count()
    total_goals = DependencyGoal.objects.count()
    total_posts = Post.objects.count()

    # --- ANALİZ 1: GRAFİK VERİSİ (Bağımlılık Dağılımı) ---
    goal_stats = DependencyGoal.objects.values('dependency_type').annotate(total=Count('id'))
    
    # JavaScript'in anlayacağı formata (JSON) çeviriyoruz
    # Grafik etiketleri ve değerleri
    chart_labels = [item['dependency_type'].capitalize() for item in goal_stats]
    chart_data = [item['total'] for item in goal_stats]

    # --- ANALİZ 2: SON AKTİVİTELER ---
    # En son kayıt olan 3 kullanıcı
    recent_users = User.objects.all().order_by('-date_joined')[:3]
    # En son açılan 3 hedef
    recent_goals = DependencyGoal.objects.select_related('user').order_by('-start_date')[:3]

    context = {
        'total_users': total_users,
        'total_goals': total_goals,
        'total_posts': total_posts,
        'chart_labels': json.dumps(chart_labels), # JSON formatında gönderiyoruz
        'chart_data': json.dumps(chart_data),
        'recent_users': recent_users,
        'recent_goals': recent_goals,
    }
    return render(request, 'yonetim/dashboard.html', context)

# --- 2. KULLANICI YÖNETİMİ (LİSTELEME, EKLEME, SİLME) ---
@staff_member_required(login_url='/gizli-admin/login/') 
def user_list(request):
    query = request.GET.get('q', '') 
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).prefetch_related('earned_badges__badge', 'goals').order_by('-date_joined')
    else:
        users = User.objects.all().prefetch_related('earned_badges__badge', 'goals').order_by('-date_joined')

    context = {'users': users, 'query': query}
    return render(request, 'yonetim/user_list.html', context)

@staff_member_required(login_url='/gizli-admin/login/')
def user_delete(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    if user_to_delete == request.user:
        messages.error(request, "Kendi yönetici hesabınızı silemezsiniz!")
    else:
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"{username} isimli kullanıcı başarıyla silindi.")
    return redirect('yonetim:user_list')

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

# --- 3. HEDEF ANALİZİ ---
@staff_member_required(login_url='/gizli-admin/login/')
def goal_list(request):
    goals = DependencyGoal.objects.all().select_related('user').order_by('-start_date')
    stats = DependencyGoal.objects.values('dependency_type').annotate(total=Count('id'))
    context = {'goals': goals, 'stats': stats}
    return render(request, 'yonetim/goal_list.html', context)

# --- 4. TOPLULUK MODERASYONU (ŞİKAYET ODAKLI) ---
@staff_member_required(login_url='/gizli-admin/login/')
def post_list(request):
    posts = Post.objects.annotate(
        report_count=Count('reports')
    ).select_related('user').prefetch_related('reports').order_by('-report_count', '-created_at')
    
    context = {'posts': posts}
    return render(request, 'yonetim/post_list.html', context)

@staff_member_required(login_url='/gizli-admin/login/')
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    title = post.title
    post.delete()
    messages.success(request, f'"{title}" başlıklı gönderi moderasyon gereği silindi.')
    return redirect('yonetim:post_list')