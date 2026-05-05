from django.contrib import admin
from .models import DependencyGoal, DailyLog, Badge, UserBadge # Modellerini buradan çağırıyoruz

# 1. BAĞIMLILIK HEDEFLERİ YÖNETİMİ
@admin.register(DependencyGoal)
class DependencyGoalAdmin(admin.ModelAdmin):
    # Tablo Sütunları: Başarı oranını da listeye ekledik
    list_display = ('user', 'dependency_type', 'initial_score', 'success_rate_display', 'is_active', 'start_date')
    
    # Sağ taraftaki filtreleme kutusu
    list_filter = ('dependency_type', 'is_active', 'start_date')
    
    # Kullanıcı adına göre arama çubuğu
    search_fields = ('user__username', 'dependency_type')
    
    # Verileri direkt listeden düzenlenebilir yapma
    list_editable = ('is_active',)

    # --- ÖZEL FONKSİYON: Başarı Oranı Hesaplama ---
    def success_rate_display(self, obj):
        # related_name='logs' sayesinde tüm kayıtlara ulaşıyoruz
        total_days = obj.logs.count()
        if total_days == 0:
            return "Veri Yok"
        clean_days = obj.logs.filter(relapse=False).count()
        rate = (clean_days / total_days) * 100
        return f"%{round(rate, 1)}"
    
    success_rate_display.short_description = "Başarı Oranı"

# 2. GÜNLÜK KAYITLAR YÖNETİMİ
@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    # Listede tarih, istek seviyesi ve bozup bozmadığını görelim
    list_display = ('goal', 'date', 'craving_level', 'relapse')
    
    # Relapse (bozulma) durumuna ve bağımlılık türüne göre filtrele
    list_filter = ('relapse', 'date', 'goal__dependency_type')
    
    # En üste takvim navigasyonu ekler
    date_hierarchy = 'date'

# 3. ROZET SİSTEMİ YÖNETİMİ
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'days_required', 'image_name')
    search_fields = ('name',)

# 4. KAZANILAN ROZETLER YÖNETİMİ
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('user__username', 'badge__name')