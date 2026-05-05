from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Post, Friendship, Notification, Comment
from tracking.models import DependencyGoal # Rozet tablosu henüz yoktu

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
            # Orijinal yapında 'author' kullanılıyordu
            Post.objects.create(author=request.user, content=content)
            return redirect('community:community_home')
    return render(request, 'community/create_post.html')

# 3. GÖNDERİ DETAY
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'community/post_detail.html', {'post': post})

# 4. KULLANICI LİSTESİ (ARKADAŞ BULMA)
@login_required
def user_list(request):
    # Sadece seni hariç tutan en sade liste
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'community/user_list.html', {'users': users})

# 5. ARKADAŞLIK İSTEKLERİ VE BİLDİRİMLER
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

# 6. PROFİL GÖRÜNTÜLEME (EN SADE HALİ)
@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Rozetler gelmeden önce sadece postlar ve hedefler vardı
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    active_goals = DependencyGoal.objects.filter(user=user, is_active=True)
    
    context = {
        'profile_user': user,
        'user_posts': user_posts,
        'active_goals': active_goals,
    }
    return render(request, 'community/user_profile.html', context)

# 7. BİLDİRİMLER SİSTEMİ
@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user, is_read=False)
    return render(request, 'community/notifications.html', {'notifications': notifs})

# 8. ARKADAŞ ÇIKARMA VE DİĞERLERİ
@login_required
def remove_friend(request, user_id):
    Friendship.objects.filter(
        (Q(from_user=request.user) & Q(to_user_id=user_id)) | 
        (Q(from_user_id=user_id) & Q(to_user=request.user))
    ).delete()
    return redirect('community:user_list')