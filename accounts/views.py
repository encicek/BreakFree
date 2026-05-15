from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# --- KAYIT OLMA (REGISTER) ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hesabınız başarıyla oluşturuldu. Giriş yapabilirsiniz.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# --- GİRİŞ YAPMA (LOGIN) - ADMİN ENGELİ EKLENDİ ---
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # 🚀 KRİTİK GÜVENLİK KONTROLÜ
                # Eğer kullanıcı admin (staff) veya süper kullanıcı ise normal girişi engelle
                if user.is_staff or user.is_superuser:
                    messages.error(request, "Yönetici hesapları bu alandan giriş yapamaz. Lütfen yönetim panelini kullanın.")
                    return redirect('login')
                
                # ✅ Sadece normal kullanıcılar içeri girebilir
                login(request, user)
                return redirect('tracking:dashboard')
            else:
                messages.error(request, "Hatalı kullanıcı adı veya şifre.")
        else:
            messages.error(request, "Lütfen bilgilerinizi kontrol edin.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})