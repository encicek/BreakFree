from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm # Standart form kullanıyoruz

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # Süper kullanıcı oluşturur gibi en sade form
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})