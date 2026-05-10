from django.db import models
from django.contrib.auth.models import User

# --- GÖNDERİ MODELİ ---
class Post(models.Model):
    ADDICTION_CHOICES = [
        ('ekran', 'Ekran Bağımlılığı'),
        ('sigara', 'Sigara Bağımlılığı'),
        ('alkol', 'Alkol Bağımlılığı'),
        ('madde', 'Madde Bağımlılığı'),
        ('general', 'Genel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    
    is_anonymous = models.BooleanField(
        default=False, 
        verbose_name="Anonim Paylaş"
    )
    
    # 🚨 FİZİKSEL KOLONLAR (Veritabanında olması gerekenler)
    is_published = models.BooleanField(
        default=True,
        verbose_name="Yayında mı?"
    )
    report_count = models.IntegerField(
        default=0, 
        verbose_name="Şikayet Sayısı"
    )
    
    # 🚨 GÜVENLİK AĞI (Property Katmanı): 
    # Eğer migration bir sebeple veritabanına yansımazsa template'ler çökmesin diye.
    @property
    def safe_is_published(self):
        return getattr(self, 'is_published', True)

    @property
    def safe_report_count(self):
        return getattr(self, 'report_count', 0)
    
    addiction_type = models.CharField(
        max_length=20,
        choices=ADDICTION_CHOICES,
        default='general',
        verbose_name="Kategori"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def total_supports(self):
        return self.supports.count()

    def total_comments(self):
        return self.comments.count()

    def __str__(self):
        return self.title

    # 🚨 GÜNCELLENDİ: Hata Toleranslı Kaydetme Mantığı
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

# --- YORUM MODELİ ---
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"

# --- DESTEK (LIKE) MODELİ ---
class Support(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='supports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} supports {self.post.title}"

# --- ARKADAŞLIK SİSTEMİ ---
class Friendship(models.Model):
    STATUS_CHOICES = (('pending', 'Beklemede'), ('accepted', 'Kabul Edildi'))
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

# --- BİLDİRİM SİSTEMİ ---
class Notification(models.Model):
    NOTIFICATION_TYPES = (('support', 'Destek'), ('comment', 'Yorum'), ('friend_request', 'Arkadaşlık İsteği'))
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# --- ŞİKAYET MODELİ ---
class Report(models.Model):
    REPORT_CHOICES = [
        ('spam', 'Spam / Gereksiz'),
        ('harassment', 'Taciz / Zorbalık'),
        ('inappropriate', 'Uygunsuz İçerik'),
        ('misleading', 'Yanıltıcı Bilgi'),
        ('other', 'Diğer'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']