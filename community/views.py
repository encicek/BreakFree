from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse

from .models import Post, Friendship
from tracking.models import DependencyGoal, DailyLog
from tracking.forms import GoalForm
from .forms import PostForm, CommentForm

@login_required
def community_home(request):
    posts = Post.objects.all().order_by('-created_at')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('community/posts_list_partial.html', {'posts': posts})
        return HttpResponse(html)
        
    return render(request, 'community/community_home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community:community_home')
    else:
        form = PostForm()
    return render(request, 'community/create_post.html', {'form': form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('community:post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()

    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def support_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    support, created = post.supports.get_or_create(user=request.user)
    if not created:
        support.delete()
    return redirect('community:post_detail', post_id=post.id)

@login_required
def user_list(request):
    search_query = request.GET.get('search')
    
    friend_ids = Friendship.objects.filter(
        from_user=request.user
    ).values_list('to_user_id', flat=True)

    users_queryset = User.objects.exclude(id=request.user.id).exclude(id__in=friend_ids)

    if search_query:
        users = users_queryset.filter(username__icontains=search_query)
    else:
        users = users_queryset

    return render(request, 'community/user_list.html', {
        'users': users,
        'search_query': search_query,
    })

# --- PROFİL SİSTEMİ: TÜM HATALARI GİDERİLMİŞ VERSİYON ---
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    # Takip Kontrolü
    following_relations = Friendship.objects.filter(from_user=profile_user)
    following_list = [rel.to_user for rel in following_relations]
    is_friend = Friendship.objects.filter(from_user=request.user, to_user=profile_user).exists()

    # Aktif Bağımlılık Hedefleri (Sol Kolon)
    active_goals = DependencyGoal.objects.filter(user=profile_user, is_active=True)
    
    # Başarı İstatistikleri İçin Varsayılan Değerler
    clean_days = 0
    badges = []
    current_status = "Aktif"
    recent_logs = []
    friend_activities = []

    if active_goals.exists():
        # ANA HEDEF ANALİZİ: İlk hedef üzerinden temiz gün hesaplama
        primary_goal = active_goals.first()
        
        # Sadece 'Bozdum' işaretlenmemiş benzersiz tarihleri sayıyoruz
        clean_days = DailyLog.objects.filter(
            goal=primary_goal, 
            relapse=False
        ).values('date').distinct().count() 
        
        # SAĞ KOLON: Kullanıcının son 5 aktivite kaydı (En yeni üstte)
        recent_logs = DailyLog.objects.filter(goal__user=profile_user).order_by('-date')[:5]

        # ROZET MANTIĞI
        if clean_days >= 1: badges.append({'name': 'İlk Adım', 'icon': '🥉'})
        if clean_days >= 7: badges.append({'name': 'Savaşçı', 'icon': '🥈'})
        if clean_days >= 30: badges.append({'name': 'Efendi', 'icon': '🥇'})

        # ANLIK DURUM ANALİZİ
        last_log = recent_logs.first()
        if last_log:
            if last_log.relapse: current_status = "Kriz Yaşadı"
            elif last_log.craving_level >= 7: current_status = "Zorlanıyor"
            else: current_status = "Güçlü"

    # ARKADAŞ HABERLERİ: Sadece kendi profilindeyse haber akışını çek
    if request.user == profile_user:
        my_follows = Friendship.objects.filter(from_user=request.user).values_list('to_user', flat=True)
        # Yol arkadaşlarının son 10 başarısını getiriyoruz
        friend_activities = DailyLog.objects.filter(
            goal__user__in=my_follows
        ).order_by('-date')[:10]

    return render(request, 'community/user_profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_friend': is_friend,
        'active_goals': active_goals,
        'clean_days': clean_days,
        'recent_logs': recent_logs,
        'following_list': following_list,
        'current_status': current_status,
        'badges': badges,
        'friend_activities': friend_activities,
    })

@login_required
def toggle_friend(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user:
        friendship, created = Friendship.objects.get_or_create(
            from_user=request.user,
            to_user=to_user
        )
        if not created:
            friendship.delete()
    return redirect(request.META.get('HTTP_REFERER', 'community:user_profile'))

@login_required
def edit_profile(request, goal_id):
    goal = get_object_or_404(DependencyGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('community:user_profile', username=request.user.username)
    else:
        form = GoalForm(instance=goal)
    
    return render(request, 'community/edit_profile.html', {'form': form})