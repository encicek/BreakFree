from django.contrib import admin
from .models import Post, Comment, Support, Friendship, Notification, Report

# --- POST YÖNETİMİ ---
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'addiction_type', 'is_anonymous', 'created_at') # Kolonlar
    list_filter = ('addiction_type', 'is_anonymous', 'created_at') # Sağdaki filtre paneli
    search_fields = ('title', 'content', 'user__username') # Arama çubuğu
    ordering = ('-created_at',) # Tersten sıralama

# --- YORUM YÖNETİMİ ---
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'post__title')

# --- DESTEK (LIKE) YÖNETİMİ ---
@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')

# --- ARKADAŞLIK / TAKİP YÖNETİMİ ---
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')

# --- 🚨 BİLDİRİM SİSTEMİ YÖNETİMİ ---
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username')

# --- 🚨 ŞİKAYET VE MODERASYON YÖNETİMİ ---
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'reason', 'is_resolved', 'created_at') # Önemli kolonlar
    list_filter = ('reason', 'is_resolved', 'created_at') # Filtreleme
    search_fields = ('post__title', 'reporter__username', 'description')
    list_editable = ('is_resolved',) # Admin listesinden direkt "Çözüldü" işaretleme özelliği
    actions = ['mark_as_resolved'] # Toplu işlemler

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = "Seçilen şikayetleri çözüldü olarak işaretle"