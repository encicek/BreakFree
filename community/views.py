import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from .models import Post, Friendship, Notification, Comment
from tracking.models import UserBadge, DependencyGoal 

# 1. TOPLULUK ANA SAYFASI
@login_required
def community_home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/home.html', {'posts': posts})

# 2. GÖNDERİ OLUŞTURMA
@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Modelindeki 'user' alanına göre kayıt yapıyoruz
            Post.objects.create(user=request.user, content=content)
            return redirect('community:community_home')
    return render(request, 'community/create_post.html')

# 3. GÖNDERİ DETAY VE DESTEK
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'community/post_detail.html', {'post': post})

@login_required
def support_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return redirect('community:post_detail', post_id=post_id)

# 4. KULLANICI LİSTESİ VE ARKADAŞLIK (ADMİN GİZLENDİ)
@login_required
def user_list(request):
    # Hem kendini hem de 'admin' isimli kullanıcıyı/süper kullanıcıları hariç tutuyoruz
    users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True).exclude(username='admin')
    return render(request, 'community/user_list.html', {'users': users})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    Friendship.objects.get_or_create(from_user=request.user, to_user=to_user, status='sent')
    Notification.objects.create(recipient=to_user, sender=request.user, notification_type='friend_request')
    return redirect('community:user_list')

@login_required
def accept_friend_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    friendship = Friendship.objects.get(from_user=notification.sender, to_user=request.user)
    friendship.status = 'accepted'
    friendship.save()
    notification.is_read = True
    notification.save()
    return redirect('community:notifications')

@login_required
def reject_friend_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    return redirect('community:notifications')

# 5. PROFİL GÖRÜNTÜLEME (KRİTİK GÜNCELLEME)
@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Takip panelindeki gerçek rozetleri çekiyoruz
    user_badges = UserBadge.objects.filter(user=user).select_related('badge').order_by('-earned_at')
    
    # Senin modelindeki 'user' alanına göre filtreliyoruz
    user_posts = Post.objects.filter(user=user).order_by('-created_at')
    
    active_goals = DependencyGoal.objects.filter(user=user, is_active=True)
    
    # Grafik ve Log verileri (Profilin hatasız açılması için şart)
    main_goal = active_goals.first()
    recent_logs = []
    chart_labels = []
    chart_data = []
    
    if main_goal:
        recent_logs = main_goal.logs.all().order_by('-date')[:5]
        chart_logs = main_goal.logs.all().order_by('date')[:10]
        chart_labels = [log.date.strftime('%d %b') for log in chart_logs]
        chart_data = [log.craving_level for log in chart_logs]

    # Arkadaşlık durumu ve listesi
    status_label = 'none'
    friendship = Friendship.objects.filter(
        (Q(from_user=request.user) & Q(to_user=user)) | 
        (Q(from_user=user) & Q(to_user=request.user))
    ).first()
    if friendship:
        status_label = friendship.status

    friends_qs = Friendship.objects.filter((Q(from_user=user) | Q(to_user=user)), status='accepted')
    friend_list = [f.to_user if f.from_user == user else f.from_user for f in friends_qs]

    context = {
        'profile_user': user,
        'user_badges': user_badges,
        'user_posts': user_posts,
        'active_goals': active_goals,
        'recent_logs': recent_logs,
        'friend_list': friend_list,
        'status_label': status_label,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'community/user_profile.html', context)

# 6. PROFİL DÜZENLEME VE DİĞERLERİ
@login_required
def edit_profile(request, goal_id):
    goal = get_object_or_404(DependencyGoal, id=goal_id, user=request.user)
    return render(request, 'community/edit_profile.html', {'goal': goal})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user, is_read=False)
    return render(request, 'community/notifications.html', {'notifications': notifs})

@login_required
def report_post(request, post_id):
    return redirect('community:community_home')

@login_required
def remove_friend(request, user_id):
    Friendship.objects.filter(
        (Q(from_user=request.user) & Q(to_user_id=user_id)) | 
        (Q(from_user_id=user_id) & Q(to_user=request.user))
    ).delete()
    return redirect('community:user_list')