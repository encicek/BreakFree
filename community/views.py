from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date

from .models import Post, Friendship
from .forms import PostForm, CommentForm
from tracking.models import DependencyGoal


def community_home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/community_home.html', {'posts': posts})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_home')
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
            return redirect('post_detail', post_id=post.id)
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

    return redirect('post_detail', post_id=post.id)

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)

    friends = Friendship.objects.filter(
        from_user=request.user
    ).values_list('to_user_id', flat=True)

    return render(request, 'community/user_list.html', {
        'users': users,
        'friends': friends,
    })


@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    is_friend = Friendship.objects.filter(
        from_user=request.user,
        to_user=profile_user
    ).exists()

    goal = DependencyGoal.objects.filter(
        user=profile_user,
        is_active=True
    ).first()

    clean_days = 0
    risk_level = None
    recent_logs = None

    monthly_success_rate = 0
    monthly_total_logs = 0
    monthly_relapses = 0
    monthly_success_days = 0

    if goal:
        relapse_count = goal.logs.filter(relapse=True).count()
        total_days = (date.today() - goal.start_date).days + 1
        clean_days = max(total_days - relapse_count, 0)

        recent_logs = goal.logs.all()[:5]

        today = date.today()
        monthly_logs = goal.logs.filter(
            date__year=today.year,
            date__month=today.month
        )

        monthly_total_logs = monthly_logs.count()
        monthly_relapses = monthly_logs.filter(relapse=True).count()
        monthly_success_days = monthly_total_logs - monthly_relapses

        if monthly_total_logs > 0:
            monthly_success_rate = round(
                (monthly_success_days / monthly_total_logs) * 100
            )

        if goal.initial_score >= 70:
            risk_level = "Yüksek"
        elif goal.initial_score >= 40:
            risk_level = "Orta"
        else:
            risk_level = "Düşük"

    return render(request, 'community/user_profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_friend': is_friend,
        'goal': goal,
        'clean_days': clean_days,
        'risk_level': risk_level,
        'recent_logs': recent_logs,
        'monthly_success_rate': monthly_success_rate,
        'monthly_total_logs': monthly_total_logs,
        'monthly_relapses': monthly_relapses,
        'monthly_success_days': monthly_success_days,
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

    return redirect('user_profile', username=to_user.username)