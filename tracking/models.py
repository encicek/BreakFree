from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Tarih işlemleri için gerekli

class DependencyGoal(models.Model):
    DEPENDENCY_CHOICES = [
        ('sigara', 'Sigara'),
        ('alkol', 'Alkol'),
        ('ekran', 'Ekran'),
        ('madde', 'Madde'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_CHOICES)
    start_date = models.DateField(auto_now_add=True)
    initial_score = models.IntegerField(help_text="Kayıt anketinden gelen başlangıç skoru (0-100)")
    target_note = models.TextField(blank=True, help_text="Kullanıcının kendine koyduğu motivasyon sözü")
    
    # YENİ EKLENEN: Kullanıcının profilinde görünecek Bio alanı
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="Yol arkadaşlarınıza kendinizden ve motivasyonunuzdan bahsedin."
    )
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_dependency_type_display()}"

class DailyLog(models.Model):
    goal = models.ForeignKey(DependencyGoal, on_delete=models.CASCADE, related_name='logs')
    
    # DÜZENLENDİ: auto_now_add=True kaldırıldı. 
    # default=timezone.now sayesinde hem otomatik dolar hem de formda manuel seçilebilir.
    date = models.DateField(default=timezone.now) 
    
    craving_level = models.IntegerField(help_text="1-10 arası zorlanma/istek seviyesi")
    relapse = models.BooleanField(default=False, help_text="Bugün kural bozuldu mu?")
    trigger = models.CharField(max_length=100, blank=True, help_text="Tetikleyici unsur")
    daily_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        # Aynı güne mükerrer kayıt girilmesini engellemek için (isteğe bağlı):
        # unique_together = ('goal', 'date')

    def __str__(self):
        return f"{self.date} | {self.goal.user.username} | Relapse: {'Evet' if self.relapse else 'Hayır'}"