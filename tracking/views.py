from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DependencyGoal, DailyLog
from .forms import GoalForm, DailyLogForm

# 1. BİLİMSEL TEMELLİ ANKET SORULARI (Değişmedi)
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

# 2. TAKİP PANELİ VE GÜNLÜK KAYIT
@login_required(login_url='/accounts/login/')
def dashboard(request):
    # Kullanıcının aktif hedefini bul
    goal = DependencyGoal.objects.filter(user=request.user, is_active=True).first()
    
    if goal:
        # 1. Temiz gün sayısını hesapla
        clean_days = goal.logs.filter(relapse=False).count()
        
        # 2. Risk Seviyesini HESAPLA (Hata buradaydı, değişkeni mutlaka tanımlıyoruz)
        if goal.initial_score > 70:
            risk_level = "Yüksek"
        elif goal.initial_score > 35:
            risk_level = "Orta"
        else:
            risk_level = "Düşük"

        # 3. Günlük kayıt formu işlemleri
        if request.method == 'POST':
            log_form = DailyLogForm(request.POST)
            if log_form.is_valid():
                log = log_form.save(commit=False)
                log.goal = goal
                log.save()
                return redirect('tracking:dashboard')
        else:
            log_form = DailyLogForm()

        # 4. Verileri sayfaya gönder
        context = {
            'goal': goal,
            'clean_days': clean_days,
            'log_form': log_form,
            'risk_level': risk_level # Buradaki risk_level artık tanımlı!
        }
        return render(request, 'tracking/dashboard.html', context)
    
    # Eğer aktif hedef yoksa butonların olduğu sayfaya yönlendir
    return render(request, 'tracking/dashboard.html', {'goal': None})
    # EĞER HEDEF YOKSA: Sadece None gönder, template otomatik {% else %}'e düşecek
    return render(request, 'tracking/dashboard.html', {'goal': None})
# 3. ANKET SİSTEMİ
@login_required(login_url='/accounts/login/') # BURAYI GÜNCELLEDİK
def survey_view(request):
    dep_type = request.GET.get('type', 'sigara')
    questions = DEPENDENCY_SURVEYS.get(dep_type, DEPENDENCY_SURVEYS['sigara'])

    if request.method == 'POST':
        total_score = 0
        max_possible_score = 0
        for q in questions:
            max_possible_score += max([int(choice[0]) for choice in q['choices']])

        for key, value in request.POST.items():
            if key.startswith('q_'):
                total_score += int(value)
        
        final_score = int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
        request.session['calculated_score'] = final_score
        request.session['chosen_type'] = dep_type
        return redirect('tracking:create_goal')
        
    return render(request, 'tracking/survey.html', {'questions': questions, 'type': dep_type})

# 4. HEDEF OLUŞTURMA
@login_required(login_url='/accounts/login/') # BURAYI GÜNCELLEDİK
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