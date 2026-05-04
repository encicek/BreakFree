from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q 
from django.core.paginator import Paginator 
from .models import Post, Friendship, Notification, Report 
from tracking.models import DependencyGoal, DailyLog, UserBadge  # UserBadge eklendi
from tracking.forms import GoalForm
from .forms import PostForm, CommentForm
import datetime
import json 

# --- TOPLULUK ANA SAYFASI ---
@login_required
def community_home(request):
    query = request.GET.get('q', '').strip() 
    category_filter = request.GET.get('category') 
    posts_list = Post.objects.all().order_by('-created_at')
    if query:
        posts_list = posts_list.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(user__username__icontains=query))
    if category_filter and category_filter != 'all':
        posts_list = posts_list.filter(addiction_type=category_filter)
    paginator = Paginator(posts_list, 10) 
    posts = paginator.get_page(request.GET.get('page'))
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('community/posts_list_partial.html', {'posts': posts})
        return HttpResponse(html)
    return render(request, 'community/community_home.html', {'posts': posts, 'current_category': category_filter, 'query': query})

# --- PROFİL SİSTEMİ (Rozet Desteği Eklendi) ---
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    # Hedef İstatistiklerini Hesapla
    raw_goals = DependencyGoal.objects.filter(user=profile_user, is_active=True)
    active_goals_with_stats = []
    for goal in raw_goals:
        last_relapse = DailyLog.objects.filter(goal=goal, relapse=True).order_by('-date').first()
        streak = DailyLog.objects.filter(goal=goal, relapse=False, date__gt=last_relapse.date).values('date').distinct().count() if last_relapse else DailyLog.objects.filter(goal=goal, relapse=False).values('date').distinct().count()
        last_log = DailyLog.objects.filter(goal=goal).order_by('-date').first()
        status = "Güçlü"
        if last_log:
            if last_log.relapse: status = "Kriz Yaşadı"
            elif last_log.craving_level >= 7: status = "Zorlanıyor"
        goal.streak = streak
        goal.status = status
        active_goals_with_stats.append(goal)

    # Arkadaşlık Durumu Kontrolü
    sent_req = Friendship.objects.filter(from_user=request.user, to_user=profile_user).first()
    received_req = Friendship.objects.filter(from_user=profile_user, to_user=request.user).first()
    
    status_label = "none"
    if sent_req:
        status_label = "friends" if sent_req.status == 'accepted' else "sent"
    elif received_req:
        status_label = "friends" if received_req.status == 'accepted' else "received"

    # Arkadaş Listesi
    friendships = Friendship.objects.filter(
        Q(from_user=profile_user, status='accepted') | 
        Q(to_user=profile_user, status='accepted')
    ).select_related('from_user', 'to_user')

    friends_set = set()
    for f in friendships:
        if f.from_user == profile_user:
            friends_set.add(f.to_user)
        else:
            friends_set.add(f.from_user)
    
    friend_list = list(friends_set)

    # --- ROZET VERİLERİ (DÜZELTME) ---
    # Kullanıcının kazandığı rozetleri tarih sırasına göre çekiyoruz
    user_badges = UserBadge.objects.filter(user=profile_user).select_related('badge').order_by('earned_at')

    # GRAFİK VERİSİ
    ten_days_logs = DailyLog.objects.filter(goal__user=profile_user).order_by('-date')[:10]
    ten_days_logs = sorted(ten_days_logs, key=lambda x: x.date) 
    
    chart_labels = [log.date.strftime("%d %b") for log in ten_days_logs]
    chart_data = [log.craving_level for log in ten_days_logs]

    # Haber Kaynağı
    friend_activities_list = []
    if request.user == profile_user:
        my_friends_ids = [u.id for u in friend_list]
        friend_activities_list = DailyLog.objects.filter(goal__user__in=my_friends_ids, relapse=False).order_by('-date')
    
    paginator = Paginator(friend_activities_list, 5)
    friend_activities = paginator.get_page(request.GET.get('friend_page'))

    recent_logs = DailyLog.objects.filter(goal__user=profile_user).order_by('-date')[:5]

    return render(request, 'community/user_profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'active_goals': active_goals_with_stats,
        'status_label': status_label,
        'friend_list': friend_list,
        'friend_activities': friend_activities,
        'recent_logs': recent_logs,
        'user_badges': user_badges,  # Context'e eklendi
        'chart_labels': json.dumps(chart_labels), 
        'chart_data': json.dumps(chart_data),     
    })

# --- ARKADAŞLIK İŞLEMLERİ ---
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user:
        exists = Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user) | 
            Q(from_user=to_user, to_user=request.user)
        ).exists()
        
        if not exists:
            Friendship.objects.create(from_user=request.user, to_user=to_user, status='pending')
            Notification.objects.create(
                recipient=to_user, sender=request.user, 
                notification_type='friend_request', post=None  
            )
    return redirect('community:user_profile', username=to_user.username)

@login_required
def accept_friend_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    sender = notification.sender
    friendship = Friendship.objects.filter(from_user=sender, to_user=request.user, status='pending').first()
    if friendship:
        friendship.status = 'accepted'
        friendship.save()
    notification.delete()
    return redirect('community:notifications')

@login_required
def reject_friend_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    Friendship.objects.filter(from_user=notification.sender, to_user=request.user, status='pending').delete()
    notification.delete()
    return redirect('community:notifications')

@login_required
def remove_friend(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=target_user) | 
        Q(from_user=target_user, to_user=request.user)
    ).delete()
    return redirect('community:user_profile', username=target_user.username)

# --- BİLDİRİMLER & KEŞFET ---
@login_required
def notifications(request):
    user_notifications = request.user.notifications.all().order_by('-created_at')
    user_notifications.exclude(notification_type='friend_request').update(is_read=True)
    return render(request, 'community/notifications.html', {'notifications': user_notifications})

@login_required
def user_list(request):
    search_query = request.GET.get('search', '').strip()
    
    # Zaten arkadaş olanları hariç tutmak için mevcut mantık
    friends_relations = Friendship.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    ).values_list('from_user_id', 'to_user_id', flat=False)

    exclude_ids = {request.user.id}
    for f_id, t_id in friends_relations:
        exclude_ids.add(f_id)
        exclude_ids.add(t_id)

    # --- KRİTİK GÜNCELLEME BURASI ---
    # is_superuser=False ekleyerek adminleri listeden tamamen çıkartıyoruz
    users_queryset = User.objects.filter(is_superuser=False).exclude(id__in=exclude_ids)
    
    if search_query:
        users = users_queryset.filter(username__icontains=search_query)
    else:
        users = users_queryset
        
    return render(request, 'community/user_list.html', {'users': users, 'search_query': search_query})

# --- STANDART İŞLEMLER ---
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
    is_supported = post.supports.filter(user=request.user).exists() if hasattr(post, 'supports') else False
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            if post.user != request.user: 
                Notification.objects.create(recipient=post.user, sender=request.user, notification_type='comment', post=post)
            return redirect('community:post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    return render(request, 'community/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form, 'is_supported': is_supported})

@login_required
def support_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    support, created = post.supports.get_or_create(user=request.user)
    if created and post.user != request.user:
        Notification.objects.create(recipient=post.user, sender=request.user, notification_type='support', post=post)
    elif not created:
        support.delete()
    return redirect(request.META.get('HTTP_REFERER', 'community:community_home'))

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description', '')
        Report.objects.create(reporter=request.user, post=post, reason=reason, description=description)
        return redirect('community:post_detail', post_id=post.id)
    return render(request, 'community/report_post.html', {'post': post})

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