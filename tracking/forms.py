from django import forms
from .models import DependencyGoal, DailyLog

class GoalForm(forms.ModelForm):
    class Meta:
        model = DependencyGoal
        # initial_score yerine bio alanı eklendi.
        fields = ['dependency_type', 'target_note', 'bio'] 
        
        widgets = {
            'dependency_type': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'target_note': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 3, 'placeholder': 'Seni ne motive eder?'}),
            'bio': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 3, 'placeholder': 'Yol arkadaşların seni tanısın...'}),
        }

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        # 'goal' alanı kayıt türünü seçmek için en başa eklendi.
        fields = ['goal', 'date', 'craving_level', 'relapse', 'trigger', 'daily_note']
        
        widgets = {
            'goal': forms.Select(attrs={'class': 'form-select rounded-pill shadow-sm'}),
            'date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
            'craving_level': forms.NumberInput(attrs={'class': 'form-control rounded-pill', 'min': 1, 'max': 10, 'placeholder': '1-10 arası'}),
            'relapse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'trigger': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Seni ne tetikledi? (Örn: Stres, Yalnızlık)'}),
            'daily_note': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 2, 'placeholder': 'Bugüne dair kısa bir not...'}),
        }

    def __init__(self, *args, **kwargs):
        # View'dan gelen 'user' bilgisi ile filtreleme yapılıyor.
        user = kwargs.pop('user', None)
        super(DailyLogForm, self).__init__(*args, **kwargs)
        
        if user:
            # SADECE mevcut kullanıcıya ait aktif hedefler listelenir.
            # Bu sayede Seda veya Kerem gibi diğer kullanıcıların hedefleri görünmez.
            self.fields['goal'].queryset = DependencyGoal.objects.filter(user=user, is_active=True)
            self.fields['goal'].empty_label = "Mücadele Seçin"
            self.fields['goal'].label = "Kayıt Girilecek Mücadele"