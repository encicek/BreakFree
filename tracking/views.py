from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import DependencyGoal, DailyLog, Badge, UserBadge
from community.models import Friendship, Notification 
from .forms import GoalForm, DailyLogForm
import datetime
import json
import random

# --- GEÇİCİ ADMİN OLUŞTURMA ---
def create_admin_account(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'sifre12345')
        return HttpResponse("Admin hesabı oluşturuldu!")
    return HttpResponse("Admin zaten mevcut.")

# 1. ANKET SORULARI
DEPENDENCY_SURVEYS = {
    'sigara': [
        {'id': 1, 'text': 'Günde ortalama kaç adet sigara tüketiyorsunuz?', 'choices': [('0', '10 veya daha az'), ('10', '11-20 adet'), ('20', '21-30 adet'), ('30', '31 ve üzeri')]},
        {'id': 2, 'text': 'Sabah uyandıktan ne kadar süre sonra ilk sigaranızı içersiniz?', 'choices': [('30', 'İlk 5 dakika içinde'), ('20', '6-30 dakika içinde'), ('10', '31-60 dakika içinde'), ('0', '1 saatten sonra')]},
        {'id': 3, 'text': 'Günün hangi sigarasından vazgeçmek sizin için en zordur?', 'choices': [('15', 'Sabah ilk içilen sigara'), ('0', 'Diğer herhangi biri')]},
        {'id': 4, 'text': 'Sigara içilmeyen yerlerde durmakta zorlanıyor musunuz?', 'choices': [('15', 'Evet'), ('0', 'Hayır')]},
        {'id': 5, 'text': 'Çok hasta olduğunuzda bile sigara içer misiniz?', 'choices': [('10', 'Evet'), ('0', 'Hayır')]},
    ],
    'alkol': [
        {'id': 1, 'text': 'Hangi sıklıkla alkol içeren bir içki tüketirsiniz?', 'choices': [('0', 'Ayda bir veya daha az'), ('10', 'Ayda 2-4 kez'), ('20', 'Haftada 2-3 kez'), ('30', 'Haftada 4 veya daha fazla')]},
        {'id': 2, 'text': 'Alkol almaya başladığınızda durmakta zorlandığınız olur mu?', 'choices': [('20', 'Her zaman'), ('10', 'Bazen'), ('0', 'Hiçbir zaman')]},
        {'id': 3, 'text': 'Normalde yapmanız gereken işleri alkol nedeniyle aksattığınız oldu mu?', 'choices': [('20', 'Haftalık'), ('10', 'Aylık'), ('0', 'Hiçbir zaman')]},
        {'id': 4, 'text': 'Güne başlamak için sabah ilk iş alkol almanız gerekti mi?', 'choices': [('20', 'Evet'), ('0', 'Hayır')]},
        {'id': 5, 'text': 'Bir yakınınız bırakmanızı önerdi mi?', 'choices': [('10', 'Evet'), ('0', 'Hayır')]},
    ],
    'ekran': [
        {'id': 1, 'text': 'Planladığınızdan daha uzun süre çevrimiçi kalıyor musunuz?', 'choices': [('20', 'Her zaman'), ('10', 'Sık sık'), ('0', 'Nadiren')]},
        {'id': 2, 'text': 'Çevrimiçi olmadığınızda huzursuz veya sinirli hissediyor musunuz?', 'choices': [('20', 'Evet, çok fazla'), ('10', 'Kısmen'), ('0', 'Hayır')]},
        {'id': 3, 'text': 'İnternet kullanımı nedeniyle sosyal ilişkilerinizde sorun yaşadınız mı?', 'choices': [('20', 'Evet, ciddi'), ('5', 'Hafif'), ('0', 'Hayır')]},
        {'id': 4, 'text': 'Stres veya çaresizlikten kaçmak için mi ekrana yöneliyorsunuz?', 'choices': [('20', 'Kesinlikle evet'), ('10', 'Bazen'), ('0', 'Hayır')]},
        {'id': 5, 'text': 'Ekranda geçirdiğiniz süreyi gizlemek için yalan söylüyor musunuz?', 'choices': [('20', 'Evet'), ('0', 'Hayır')]},
    ],
    'madde': [
        {'id': 1, 'text': 'Maddeyi planladığınızdan daha büyük miktarlarda mı kullanıyorsunuz?', 'choices': [('25', 'Evet'), ('0', 'Hayır')]},
        {'id': 2, 'text': 'Kontrol altına almak için başarısız girişimleriniz oldu mu?', 'choices': [('25', 'Evet'), ('0', 'Hayır')]},
        {'id': 3, 'text': 'Maddeyi bulmak veya kullanmak için çok fazla zaman harcıyor musunuz?', 'choices': [('25', 'Evet'), ('0', 'Hayır')]},
        {'id': 4, 'text': 'Önemli etkinliklerden madde kullanımı için vazgeçtiniz mi?', 'choices': [('25', 'Evet'), ('0', 'Hayır')]},
    ]
}

# --- ROZET KONTROL FONKSİYONU ---
def check_and_assign_badges(user, goal, streak):
    # Kullanıcının kazandığı rozetleri belirliyoruz
    available_badges = Badge.objects.filter(days_required__lte=streak)
    for badge in available_badges:
        calculated_date = goal.start_date + datetime.timedelta(days=badge.days_required)
        
        if calculated_date > datetime.date.today():
            calculated_date = datetime.date.today()

        UserBadge.objects.update_or_create(
            user=user, 
            badge=badge,
            defaults={'earned_at': calculated_date}
        )

# 2. DASHBOARD
@login_required(login_url='/accounts/login/')
def dashboard(request):
    all_active_goals = DependencyGoal.objects.filter(user=request.user, is_active=True)
    existing_types = all_active_goals.values_list('dependency_type', flat=True)
    
    goal_id = request.GET.get('goal_id')
    current_month = int(request.GET.get('month', datetime.date.today().month))
    current_year = int(request.GET.get('year', datetime.date.today().year))

    if goal_id:
        goal = get_object_or_404(DependencyGoal, id=goal_id, user=request.user)
    else:
        goal = all_active_goals.order_by('-id').first()
    
    # Yeni hedef modu kontrolü
    if not goal or request.GET.get('new_goal') == 'true':
        return render(request, 'tracking/dashboard.html', {
            'goal': None, 
            'all_active_goals': all_active_goals,
            'new_goal_mode': True,
            'dependency_choices': DEPENDENCY_SURVEYS.keys()
        })

    today = datetime.date.today()
    start_of_month = datetime.date(current_year, current_month, 1)
    
    if current_month == 12:
        end_of_month = datetime.date(current_year + 1, 1, 1)
    else:
        end_of_month = datetime.date(current_year, current_month + 1, 1)
    
    # Seri Hesaplama
    last_relapse = goal.logs.filter(relapse=True).order_by('-date').first()
    if last_relapse:
        current_streak = goal.logs.filter(relapse=False, date__gt=last_relapse.date).values('date').distinct().count()
    else:
        current_streak = goal.logs.filter(relapse=False).values('date').distinct().count()
    
    # Veri Girişi ve Rozet Atama
    if request.method == 'POST':
        log_form = DailyLogForm(request.POST, user=request.user)
        if log_form.is_valid():
            log = log_form.save(commit=False)
            log.save()
            check_and_assign_badges(request.user, goal, current_streak)
            return redirect(f'/tracking/dashboard/?goal_id={log.goal.id}&month={current_month}')
    else:
        check_and_assign_badges(request.user, goal, current_streak)
        log_form = DailyLogForm(initial={'date': today, 'goal': goal}, user=request.user)

    # Rozetleri çekiyoruz (Hem profil hem dashboard aynı yere bakıyor)
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge').order_by('-earned_at')
    
    current_month_logs = goal.logs.filter(date__gte=start_of_month, date__lt=end_of_month).order_by('date')
    monthly_clean_count = current_month_logs.filter(relapse=False).values('date').distinct().count()
    days_in_month = (end_of_month - start_of_month).days
    success_rate = int((monthly_clean_count / days_in_month) * 100) if days_in_month > 0 else 0

    analysis_options = {
        "level_1": ["Vücudun dopamin dengesini yeniden kurmaya başladı!", "Beynindeki Prefrontal Korteks direksiyonun başında!"],
        "level_2": ["İraden bir kas gibi güçleniyor!", "Beyninde nöroplastisite gerçekleşiyor!"],
        "level_3": ["Amigdala şu an biraz gürültülü olabilir.", "Stratejini değiştirme zamanı gelmiş olabilir."]
    }

    if success_rate >= 90:
        report_title, report_color = "Mükemmel İstikrar", "success"
        report_text = random.choice(analysis_options["level_1"])
    elif success_rate >= 70:
        report_title, report_color = "Güçlü Gelişim", "info"
        report_text = random.choice(analysis_options["level_2"])
    else:
        report_title, report_color = "Dikkat: Riskli Bölge", "warning"
        report_text = random.choice(analysis_options["level_3"])

    chart_labels = [log.date.strftime('%d %b') for log in current_month_logs]
    chart_data = [log.craving_level for log in current_month_logs]
    avg_craving = sum(chart_data) / len(chart_data) if chart_data else 0
    
    total_clean_days = goal.logs.filter(relapse=False).values('date').distinct().count()
    if total_clean_days >= 30: bio_status = "Tam Onarım"
    elif total_clean_days >= 7: bio_status = "Hücresel Yenilenme"
    elif total_clean_days >= 1: bio_status = "Onarım Başladı"
    else: bio_status = "Stabilizasyon"

    has_entry_today = goal.logs.filter(date=today).exists()
    risk_level = "Yüksek" if goal.initial_score > 70 else "Orta" if goal.initial_score > 35 else "Düşük"

    context = {
        'goal': goal, 'all_active_goals': all_active_goals, 'existing_types': list(existing_types),
        'clean_days': current_streak, 'monthly_count': monthly_clean_count, 'success_rate': success_rate,
        'risk_level': risk_level, 'log_form': log_form, 'current_month': current_month, 'current_year': current_year,
        'chart_labels': json.dumps(chart_labels), 'chart_data': json.dumps(chart_data),
        'report_title': report_title, 'report_text': report_text, 'report_color': report_color,
        'avg_craving': round(avg_craving, 1), 'bio_status': bio_status, 'user_badges': user_badges,
        'has_entry_today': has_entry_today, 'prev_month': 12 if current_month == 1 else current_month - 1,
        'next_month': 1 if current_month == 12 else current_month + 1,
        'dependency_choices': DEPENDENCY_SURVEYS.keys()
    }
    return render(request, 'tracking/dashboard.html', context)

# 3. SOS, Survey ve Create Goal
@login_required(login_url='/accounts/login/')
def send_crisis_notification(request):
    if request.method == 'POST':
        try:
            friends_qs = Friendship.objects.filter((Q(from_user=request.user) | Q(to_user=request.user)), status='accepted')
            friends_list = list(friends_qs)
            if friends_list:
                selected_friendship = random.choice(friends_list)
                target_user = selected_friendship.to_user if selected_friendship.from_user == request.user else selected_friendship.from_user
                Notification.objects.create(recipient=target_user, sender=request.user, notification_type='support', post=None, is_read=False)
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'no_friends'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid_method'}, status=400)

@login_required(login_url='/accounts/login/')
def survey_view(request):
    dep_type = request.GET.get('type', 'sigara')
    questions = DEPENDENCY_SURVEYS.get(dep_type, DEPENDENCY_SURVEYS['sigara'])
    if request.method == 'POST':
        total_score = 0
        max_possible_score = 0
        for q in questions:
            max_possible_score += max([int(choice[0]) for choice in q['choices']])
        for key, value in request.POST.items():
            if key.startswith('q_'): total_score += int(value)
        final_score = int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
        request.session['calculated_score'] = final_score
        request.session['chosen_type'] = dep_type
        return redirect('tracking:create_goal')
    return render(request, 'tracking/survey.html', {'questions': questions, 'type': dep_type})

@login_required(login_url='/accounts/login/')
def create_goal(request):
    initial_score = request.session.get('calculated_score')
    chosen_type = request.session.get('chosen_type')
    if initial_score is None: 
        return redirect('/tracking/dashboard/?new_goal=true')
    existing_goal = DependencyGoal.objects.filter(user=request.user, dependency_type=chosen_type).first()
    if request.method == 'POST':
        if existing_goal:
            if int(initial_score) > 0: existing_goal.initial_score = int(initial_score)
            existing_goal.is_active = True
            existing_goal.save()
        else:
            form = GoalForm(request.POST)
            if form.is_valid():
                goal = form.save(commit=False)
                goal.user = request.user
                goal.dependency_type = chosen_type
                goal.initial_score = int(initial_score)
                goal.save()
        request.session.pop('calculated_score', None)
        request.session.pop('chosen_type', None)
        return redirect('tracking:dashboard')
    else:
        form = GoalForm(initial={'dependency_type': chosen_type})
    return render(request, 'tracking/create_goal.html', {'form': form, 'score': initial_score, 'exists': existing_goal, 'type': chosen_type})