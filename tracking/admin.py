from django.contrib import admin
from .models import DependencyGoal, DailyLog
from .models import Badge, UserBadge

admin.site.register(Badge)
admin.site.register(UserBadge)

admin.site.register(DependencyGoal)
admin.site.register(DailyLog)