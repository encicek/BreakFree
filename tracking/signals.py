# tracking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DailyLog, Badge, UserBadge

@receiver(post_save, sender=DailyLog)
def check_badges(sender, instance, created, **kwargs):
    # Sadece yeni bir log oluşturulduğunda ve bu bir 'relapse' (bozma) değilse çalış
    if created and not instance.relapse:
        user = instance.goal.user
        goal = instance.goal

        # Mevcut seriyi (streak) hesapla
        last_relapse = goal.logs.filter(relapse=True).order_by('-date').first()
        if last_relapse:
            streak = goal.logs.filter(relapse=False, date__gt=last_relapse.date).values('date').distinct().count()
        else:
            streak = goal.logs.filter(relapse=False).values('date').distinct().count()

        # Kullanıcının şu anki serisine uygun olan tüm rozetleri çek
        potential_badges = Badge.objects.filter(days_required__lte=streak)
        
        # Bu rozetleri kullanıcıya ata (daha önce almadıysa)
        for badge in potential_badges:
            UserBadge.objects.get_or_create(user=user, badge=badge)