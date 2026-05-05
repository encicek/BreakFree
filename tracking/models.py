from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- HEDEF VE LOG MODELLERİ ---

class DependencyGoal(models.Model):
    DEPENDENCY_CHOICES = [
        ('sigara', 'Sigara'),
        ('alkol', 'Alkol'),
        ('ekran', 'Ekran'),
        ('madde', 'Madde'),
    ]
    
    # related_name='goals' sayesinde admin panelinde kullanıcı üzerinden hedeflere ulaşabileceğiz
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_CHOICES)
    start_date = models.DateField(auto_now_add=True)
    initial_score = models.IntegerField(help_text="Kayıt anketinden gelen başlangıç skoru (0-100)")
    target_note = models.TextField(blank=True, help_text="Kullanıcının kendine koyduğu motivasyon sözü")
    
    # Kullanıcı profil bio alanı
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="Yol arkadaşlarınıza kendinizden ve motivasyonunuzdan bahsedin."
    )
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_dependency_type_display()}"

class DailyLog(models.Model):
    # related_name='logs' admin panelindeki başarı oranı hesaplaması için KRİTİKTİR
    goal = models.ForeignKey(DependencyGoal, on_delete=models.CASCADE, related_name='logs')
    
    # default=timezone.now hem otomatik tarih atar hem de geçmişe dönük kayıt imkanı sağlar
    date = models.DateField(default=timezone.now) 
    
    craving_level = models.IntegerField(help_text="1-10 arası zorlanma/istek seviyesi")
    relapse = models.BooleanField(default=False, help_text="Bugün kural bozuldu mu?")
    trigger = models.CharField(max_length=100, blank=True, help_text="Tetikleyici unsur")
    daily_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        # Aynı gün için sadece bir kayıt girilmesini istersen aşağıdaki satırı yorumdan çıkarabilirsin:
        # unique_together = ('goal', 'date')

    def __str__(self):
        return f"{self.date} | {self.goal.user.username} | Relapse: {'Evet' if self.relapse else 'Hayır'}"


# --- ROZET SİSTEMİ MODELLERİ (GAMIFICATION) ---

class Badge(models.Model):
    """
    Sistemde tanımlı olan genel rozetler (7 Gün, 30 Gün vb.)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="Rozetin bilimsel veya motivasyonel açıklaması")
    
    # Görsel dosya yolu veya emoji için
    image_name = models.CharField(max_length=50, help_text="İkon için emoji veya dosya adı (örn: 🛡️)")
    
    days_required = models.IntegerField(help_text="Bu rozeti almak için gereken kesintisiz gün sayısı")

    def __str__(self):
        return f"{self.name} ({self.days_required} Gün)"

class UserBadge(models.Model):
    """
    Kullanıcıların kazandığı rozetleri eşleştiren ara tablo
    """
    # related_name='earned_badges' kullanıcı profilinde rozetleri listelerken kolaylık sağlar
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge') # Bir kullanıcı bir rozeti bir kez alabilir
        verbose_name = "Kazanılan Rozet"
        verbose_name_plural = "Kazanılan Rozetler"

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"