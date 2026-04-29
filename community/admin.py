from django.contrib import admin
from .models import Post, Comment, Support, Friendship

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Support)
admin.site.register(Friendship)