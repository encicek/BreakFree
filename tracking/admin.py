from django.contrib import admin
from .models import DependencyGoal, DailyLog

admin.site.register(DependencyGoal)
admin.site.register(DailyLog)