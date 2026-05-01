from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DependencyGoal, DailyLog
from .forms import GoalForm, DailyLogForm
import datetime
import json

# 1. BİLİMSEL TEMELLİ ANKET SORULARI
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

# 2. AYLIk ANALİZ VE DASHBOARD
@login_required(login_url='/accounts/login/')
def dashboard(request):
    goal = DependencyGoal.objects.filter(user=request.user, is_active=True).first()
    
    if goal:
        today = datetime.date.today()
        start_of_month = today.replace(day=1)
        
        # 1. Genel Seri (GÜNCELLEME: Aynı gün girilen çoklu kayıtları TEK gün sayar)
        total_clean_days = goal.logs.filter(relapse=False).values('date').distinct().count()
        
        # 2. Aylık Veriler (GÜNCELLEME: Aylık sayacı da benzersiz günlere göre güncelledik)
        current_month_logs = goal.logs.filter(date__gte=start_of_month)
        monthly_clean_unique = current_month_logs.filter(relapse=False).values('date').distinct().count()
        
        display_monthly_count = monthly_clean_unique if monthly_clean_unique <= 30 else 30
        success_rate = int((display_monthly_count / 30) * 100)

        # 3. Grafik Verisi (Son 30 kayıt - Burada tüm kayıtlar görünebilir, trend analizi için)
        last_logs = goal.logs.all().order_by('date')[:30]
        chart_labels = [log.date.strftime('%d %b') for log in last_logs]
        chart_data = [log.craving_level for log in last_logs]

        # 4. PROFESYONEL ANALİZ VE RAPORLAMA MANTIĞI
        avg_craving = sum(chart_data) / len(chart_data) if chart_data else 0
        
        if success_rate >= 90:
            report_title = "Mükemmel İstikrar"
            report_text = f"Bu ay %{success_rate} başarı oranıyla vücuduna harika bir hediye verdin. Hücrelerin yenileniyor ve iraden çelikleşiyor. 30 günün üzerinde temiz kalarak bağımlılığın nörolojik zincirlerini büyük oranda kırdın."
            report_color = "success"
        elif success_rate >= 70:
            report_title = "Güçlü Gelişim"
            report_text = f"Bu ay %{success_rate} oranında temiz kaldın. Bazı zor anların olsa da genel tabloda kazanan sensin. Ortalama zorlanma seviyen {avg_craving:.1f}/10. Bu, zihninin hala savaştığını ama pes etmediğini gösteriyor."
            report_color = "info"
        else:
            report_title = "Dikkat: Riskli Bölge"
            report_text = f"Bu ayki %{success_rate} başarı oranı, tetikleyicilerin seni zorladığını gösteriyor. Kendine verdiğin zararı minimize etmek için notlarını incele ve seni neyin geriye ittiğini analiz et."
            report_color = "warning"

        # Risk Seviyesi (Anket bazlı)
        if goal.initial_score > 70: risk_level = "Yüksek"
        elif goal.initial_score > 35: risk_level = "Orta"
        else: risk_level = "Düşük"

        if request.method == 'POST':
            log_form = DailyLogForm(request.POST)
            if log_form.is_valid():
                log = log_form.save(commit=False)
                log.goal = goal
                log.save()
                return redirect('tracking:dashboard')
        else:
            log_form = DailyLogForm()

        context = {
            'goal': goal,
            'clean_days': total_clean_days,
            'success_rate': success_rate,
            'monthly_count': display_monthly_count,
            'risk_level': risk_level,
            'log_form': log_form,
            'current_month_name': today.strftime('%B'),
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'report_title': report_title,
            'report_text': report_text,
            'report_color': report_color,
            'avg_craving': round(avg_craving, 1),
        }
        return render(request, 'tracking/dashboard.html', context)
    
    return render(request, 'tracking/dashboard.html', {'goal': None})

# 3. ANKET SİSTEMİ
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

# 4. HEDEF OLUŞTURMA
@login_required(login_url='/accounts/login/')
def create_goal(request):
    initial_score = request.session.get('calculated_score', 0)
    chosen_type = request.session.get('chosen_type', 'sigara')
    if request.method == 'POST':
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
        form = GoalForm(initial={'dependency_type': chosen_type, 'initial_score': initial_score})
    return render(request, 'tracking/create_goal.html', {'form': form, 'score': initial_score})