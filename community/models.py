from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    ADDICTION_CHOICES = [
        ('smoking', 'Smoking'),
        ('alcohol', 'Alcohol'),
        ('gaming', 'Gaming'),
        ('screen_time', 'Screen Time'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    addiction_type = models.CharField(
        max_length=20,
        choices=ADDICTION_CHOICES,
        default='general'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total_supports(self):
        return self.supports.count()

    def total_comments(self):
        return self.comments.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class Support(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='supports'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} supports {self.post.title}"
