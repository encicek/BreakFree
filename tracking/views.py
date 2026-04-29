from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DependencyGoal, DailyLog
from .forms import GoalForm, DailyLogForm

# Kullanıcının giriş yapmış olmasını zorunlu kılıyoruz
@login_required(login_url='/admin/login/') 
def dashboard(request):
    # Kullanıcının aktif hedefini bul
    goal = DependencyGoal.objects.filter(user=request.user, is_active=True).first()
    clean_days = 0
    
    # Veri analizi / Temiz gün hesaplama mantığı
    if goal:
        # Relapse (Kural bozma) durumunun False olduğu günleri sayıyoruz
        clean_days = goal.logs.filter(relapse=False).count()

    context = {
        'goal': goal,
        'clean_days': clean_days,
    }
    return render(request, 'tracking/dashboard.html', context)

@login_required(login_url='/admin/login/')
def create_goal(request):
    # Eğer kullanıcı formu doldurup Gönder'e bastıysa (POST isteği)
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            # Formu veritabanına kaydetmeden önce durduruyoruz (commit=False)
            goal = form.save(commit=False)
            # Çünkü bu hedefin HANGİ kullanıcıya ait olduğunu sisteme söylememiz lazım
            goal.user = request.user 
            goal.save() # Şimdi kaydedebiliriz!
            return redirect('tracking:dashboard') # Kaydedince paneline geri dönsün
    else:
        # Sayfaya ilk defa giriyorsa boş formu göster
        form = GoalForm()
    
    return render(request, 'tracking/create_goal.html', {'form': form})