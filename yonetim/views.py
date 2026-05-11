from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from tracking.models import DependencyGoal
from community.models import Post

@staff_member_required(login_url='/gizli-admin/login/') 
def dashboard(request):
    # Veritabanından İstatistikleri Çekiyoruz
    total_users = User.objects.count()
    total_goals = DependencyGoal.objects.count()
    total_posts = Post.objects.count()

    context = {
        'total_users': total_users,
        'total_goals': total_goals,
        'total_posts': total_posts,
    }
    
    return render(request, 'yonetim/dashboard.html', context)