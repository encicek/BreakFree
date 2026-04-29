from django import forms
from .models import DependencyGoal, DailyLog

class GoalForm(forms.ModelForm):
    class Meta:
        model = DependencyGoal
        fields = ['dependency_type', 'initial_score', 'target_note']
        widgets = {
            'dependency_type': forms.Select(attrs={'class': 'form-select'}),
            'initial_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0-100 arası test skorunuz'}),
            'target_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kendinize bir motivasyon notu bırakın...'}),
        }

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ['craving_level', 'relapse', 'trigger', 'daily_note']
        widgets = {
            'craving_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'relapse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'trigger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sizi ne tetikledi? (Örn: Stres)'}),
            'daily_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }