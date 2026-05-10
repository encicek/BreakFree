from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q 
from django.core.paginator import Paginator 
from .models import Post, Friendship, Notification, Report, Support # Support eklendi
from tracking.models import DependencyGoal, DailyLog, UserBadge
from tracking.forms import GoalForm
from .forms import PostForm, CommentForm
import datetime
import json 

# --- TOPLULUK ANA SAYFASI ---
@login_required
def community_home(request):
    query = request.GET.get('q', '').strip() 
    category_filter = request.GET.get('category') 
    
    try:
        posts_list = Post.objects.filter(is_published=True).order_by('-created_at')
    except:
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

# --- PROFİL SİSTEMİ ---
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    try:
        posts = Post.objects.filter(user=profile_user, is_published=True).order_by('-created_at')
    except:
        posts = Post.objects.filter(user=profile_user).order_by('-created_at')

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

    sent_req = Friendship.objects.filter(from_user=request.user, to_user=profile_user).first()
    received_req = Friendship.objects.filter(from_user=profile_user, to_user=request.user).first()
    status_label = "none"
    if sent_req: status_label = "friends" if sent_req.status == 'accepted' else "sent"
    elif received_req: status_label = "friends" if received_req.status == 'accepted' else "received"

    friendships = Friendship.objects.filter(Q(from_user=profile_user, status='accepted') | Q(to_user=profile_user, status='accepted')).select_related('from_user', 'to_user')
    friend_list = [f.to_user if f.from_user == profile_user else f.from_user for f in friendships]

    user_badges = UserBadge.objects.filter(user=profile_user).select_related('badge').order_by('earned_at')
    ten_days_logs = sorted(DailyLog.objects.filter(goal__user=profile_user).order_by('-date')[:10], key=lambda x: x.date) 
    chart_labels = [log.date.strftime("%d %b") for log in ten_days_logs]
    chart_data = [log.craving_level for log in ten_days_logs]

    friend_activities_list = DailyLog.objects.filter(goal__user__in=[u.id for u in friend_list], relapse=False).order_by('-date') if request.user == profile_user else []
    friend_activities = Paginator(friend_activities_list, 5).get_page(request.GET.get('friend_page'))
    recent_logs = DailyLog.objects.filter(goal__user=profile_user).order_by('-date')[:5]

    return render(request, 'community/user_profile.html', {
        'profile_user': profile_user, 'posts': posts, 'active_goals': active_goals_with_stats, 'status_label': status_label,
        'friend_list': friend_list, 'friend_activities': friend_activities, 'recent_logs': recent_logs,
        'user_badges': user_badges, 'chart_labels': json.dumps(chart_labels), 'chart_data': json.dumps(chart_data),     
    })

# --- ARKADAŞLIK & BİLDİRİM (Hata Veren Kısımlar Düzenlendi) ---
@login_required
def notifications(request):
    user_notifications = request.user.notifications.all().order_by('-created_at')
    user_notifications.exclude(notification_type='friend_request').update(is_read=True)
    return render(request, 'community/notifications.html', {'notifications': user_notifications})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user:
        if not Friendship.objects.filter(Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user)).exists():
            Friendship.objects.create(from_user=request.user, to_user=to_user, status='pending')
            Notification.objects.create(recipient=to_user, sender=request.user, notification_type='friend_request')
    return redirect('community:user_profile', username=to_user.username)

@login_required
def accept_friend_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    friendship = Friendship.objects.filter(from_user=notification.sender, to_user=request.user, status='pending').first()
    if friendship:
        friendship.status = 'accepted'
        friendship.save()
    notification.delete()
    # 🚨 Reverse hatasına karşı önlem:
    try: return redirect('community:notifications')
    except: return redirect('community:community_home')

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')
    
    # supports hatasına karşı kesin çözüm:
    try: is_supported = post.supports.filter(user=request.user).exists()
    except: is_supported = False
        
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post, comment.user = post, request.user
            comment.save()
            if post.user != request.user: 
                Notification.objects.create(recipient=post.user, sender=request.user, notification_type='comment', post=post)
            return redirect('community:post_detail', post_id=post.id)
    return render(request, 'community/post_detail.html', {'post': post, 'comments': comments, 'comment_form': CommentForm(), 'is_supported': is_supported})

@login_required
def support_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        support, created = Support.objects.get_or_create(post=post, user=request.user)
        if created and post.user != request.user:
            Notification.objects.create(recipient=post.user, sender=request.user, notification_type='support', post=post)
        elif not created: support.delete()
    except: pass
    return redirect(request.META.get('HTTP_REFERER', 'community:community_home'))

# --- DİĞERLERİ ---
@login_required
def user_list(request):
    search_query = request.GET.get('search', '').strip()
    exclude_ids = {request.user.id}
    for f in Friendship.objects.filter(Q(from_user=request.user) | Q(to_user=request.user)):
        exclude_ids.add(f.from_user_id); exclude_ids.add(f.to_user_id)
    users = User.objects.filter(is_superuser=False).exclude(id__in=exclude_ids)
    if search_query: users = users.filter(username__icontains=search_query)
    return render(request, 'community/user_list.html', {'users': users, 'search_query': search_query})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community:community_home')
    return render(request, 'community/create_post.html', {'form': PostForm()})

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        Report.objects.create(reporter=request.user, post=post, reason=request.POST.get('reason'), description=request.POST.get('description', ''))
        return redirect('community:post_detail', post_id=post.id)
    return render(request, 'community/report_post.html', {'post': post})

@login_required
def edit_profile(request, goal_id):
    goal = get_object_or_404(DependencyGoal, id=goal_id, user=request.user)
    form = GoalForm(request.POST or None, instance=goal)
    if form.is_valid():
        form.save()
        return redirect('community:user_profile', username=request.user.username)
    return render(request, 'community/edit_profile.html', {'form': form})