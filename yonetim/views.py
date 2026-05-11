from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from tracking.models import DependencyGoal, DailyLog
from community.models import Post
import json

# --- 1. ANA PANEL (DASHBOARD) ODAKLI RİSK ANALİZİ ---
@staff_member_required(login_url='/gizli-admin/login/') 
def dashboard(request):
    # Temel Sayılar
    total_users = User.objects.count()
    total_goals = DependencyGoal.objects.count()
    total_posts = Post.objects.count()

    # --- 🚨 KRİTİK UYARI ALGORİTMASI ---
    iki_gun_once = timezone.now() - timedelta(days=2)
    
    # 1. Yüksek İstek Riski: Son 2 günde craving_level ortalaması 8+ olanlar
    high_craving_users = DailyLog.objects.filter(
        date__gte=iki_gun_once
    ).values('goal__user__username', 'goal__user__id').annotate(
        avg_craving=Avg('craving_level')
    ).filter(avg_craving__gte=8)

    # 2. Kopma Riski: Son 3 gündür hiç rapor girmeyen aktif hedefler
    uc_gun_once = timezone.now() - timedelta(days=3)
    inactive_users = DependencyGoal.objects.filter(
        is_active=True
    ).exclude(
        logs__date__gte=uc_gun_once
    ).select_related('user')[:5]

    # GRAFİK VERİSİ
    goal_stats = DependencyGoal.objects.values('dependency_type').annotate(total=Count('id'))
    chart_labels = [item['dependency_type'].capitalize() for item in goal_stats]
    chart_data = [item['total'] for item in goal_stats]

    # SON AKTİVİTELER
    recent_users = User.objects.all().order_by('-date_joined')[:3]
    recent_goals = DependencyGoal.objects.select_related('user').order_by('-start_date')[:3]

    context = {
        'total_users': total_users,
        'total_goals': total_goals,
        'total_posts': total_posts,
        'high_craving_users': high_craving_users,
        'inactive_users': inactive_users,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'recent_users': recent_users,
        'recent_goals': recent_goals,
    }
    return render(request, 'yonetim/dashboard.html', context)

# --- 2. KULLANICI YÖNETİMİ ---
@staff_member_required(login_url='/gizli-admin/login/') 
def user_list(request):
    query = request.GET.get('q', '') 
    if query:
        users = User.objects.filter(
            Q(username__icontains=query)
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
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten sistemde kayıtlı.")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, f"{username} kullanıcısı başarıyla oluşturuldu.")
    return redirect('yonetim:user_list')

# --- 3. HEDEF ANALİZİ ---
@staff_member_required(login_url='/gizli-admin/login/')
def goal_list(request):
    goals = DependencyGoal.objects.all().select_related('user').order_by('-start_date')
    stats = DependencyGoal.objects.values('dependency_type').annotate(total=Count('id'))
    context = {'goals': goals, 'stats': stats}
    return render(request, 'yonetim/goal_list.html', context)

# --- 4. TOPLULUK MODERASYONU ---
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

# --- 5. AKILLI BAŞARI TAKİBİ ---
@staff_member_required(login_url='/gizli-admin/login/')
def success_tracking(request):
    user_id = request.GET.get('user_id')
    query = request.GET.get('q', '')

    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        logs = DailyLog.objects.filter(goal__user=selected_user).order_by('-date')
        context = {
            'mode': 'detail',
            'selected_user': selected_user,
            'logs': logs
        }
    else:
        user_summaries = User.objects.annotate(
            log_count=Count('goals__logs'),
            avg_craving=Avg('goals__logs__craving_level'),
            relapse_total=Count('goals__logs', filter=Q(goals__logs__relapse=True))
        ).filter(log_count__gt=0).order_by('-log_count')

        if query:
            user_summaries = user_summaries.filter(username__icontains=query)

        context = {
            'mode': 'summary',
            'user_summaries': user_summaries,
            'query': query,
            'total_system_logs': DailyLog.objects.count()
        }
    
    return render(request, 'yonetim/success_tracking.html', context)