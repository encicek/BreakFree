from django import forms
from .models import DependencyGoal, DailyLog

class GoalForm(forms.ModelForm):
    class Meta:
        model = DependencyGoal
        # initial_score'u mantıklı bulmadığın için çıkardık, bio eklendi.
        fields = ['dependency_type', 'target_note', 'bio'] 
        
        widgets = {
            'dependency_type': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'target_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Seni ne motive eder?'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Yol arkadaşların seni tanısın...'}),
        }

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        # 'goal' alanını en başa ekledik ki kayıt hangi bağımlılığa gidecek seçilsin
        fields = ['goal', 'date', 'craving_level', 'relapse', 'trigger', 'daily_note']
        
        widgets = {
            'goal': forms.Select(attrs={'class': 'form-select rounded-pill shadow-sm'}),
            'date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
            'craving_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10, 'placeholder': '1-10 arası'}),
            'relapse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'trigger': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Tetikleyici (Örn: Stres)'}),
            'daily_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Kısa bir not...'}),
        }

    def __init__(self, *args, **kwargs):
        # View'dan gönderdiğimiz 'user' bilgisini burada yakalıyoruz
        user = kwargs.pop('user', None)
        super(DailyLogForm, self).__init__(*args, **kwargs)
        
        if user:
            # 🚨 GÜVENLİK DÜZELTMESİ: 
            # Veritabanındaki tüm hedefleri değil, SADECE bu kullanıcıya ait olanları çekiyoruz.
            # Seda veya Kerem'in hedefleri artık senin listende görünmeyecek.
            self.fields['goal'].queryset = DependencyGoal.objects.filter(user=user, is_active=True)
            self.fields['goal'].empty_label = "Mücadele Seçin"
            self.fields['goal'].label = "Kayıt Girilecek Mücadele"