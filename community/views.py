from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from .models import Post, Friendship, Notification, Comment
from tracking.models import UserBadge, DependencyGoal  # Takip panelinden veri çekmek için

# 1. TOPLULUK ANA SAYFASI
@login_required
def community_home(request):
    # Takip ettiğimiz kişilerin ve kendimizin gönderileri
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/home.html', {'posts': posts})

# 2. GÖNDERİ OLUŞTURMA
@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Post.objects.create(author=request.user, content=content)
            return redirect('community:community_home')
    return render(request, 'community/create_post.html')

# 3. GÖNDERİ DETAY VE DESTEK (LIKE)
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'community/post_detail.html', {'post': post})

@login_required
def support_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Destek mekanizması kodların buraya gelecek
    return redirect('community:post_detail', post_id=post_id)

# 4. KULLANICI LİSTESİ VE ARKADAŞLIK İSTEKLERİ
@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
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

# 5. PROFİL GÖRÜNTÜLEME (GÜNCELLENEN KISIM)
@login_required
def user_profile(request, username):
    # Profili görüntülenen kullanıcıyı bul
    user = get_object_or_404(User, username=username)
    
    # --- ROZET EŞİTLEME GÜNCELLEMESİ ---
    # Takip panelindeki (tracking) gerçek rozetleri çekiyoruz
    user_badges = UserBadge.objects.filter(user=user).select_related('badge').order_by('-earned_at')
    
    # Kullanıcının aktif hedefleri ve gönderileri
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    active_goals = DependencyGoal.objects.filter(user=user, is_active=True)
    
    context = {
        'profile_user': user,
        'user_badges': user_badges,  # HTML'de image_397883.png'deki statik rozetlerin yerine geçecek
        'user_posts': user_posts,
        'active_goals': active_goals,
    }
    return render(request, 'community/user_profile.html', context)

# 6. PROFİL DÜZENLEME
@login_required
def edit_profile(request, goal_id):
    goal = get_object_or_404(DependencyGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        # Profil ve hedef düzenleme mantığın
        pass
    return render(request, 'community/edit_profile.html', {'goal': goal})

# 7. BİLDİRİMLER VE DİĞER İŞLEMLER
@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user, is_read=False)
    return render(request, 'community/notifications.html', {'notifications': notifs})

@login_required
def report_post(request, post_id):
    # Raporlama mantığı
    return redirect('community:community_home')

@login_required
def remove_friend(request, user_id):
    # Arkadaş çıkarma mantığı
    return redirect('community:user_list')