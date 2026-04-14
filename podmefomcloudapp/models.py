from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Track(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонён'),
    ]
    CATEGORY_CHOICES = [
        ('track', 'Track'),
        ('beat', 'Beat'),
    ]

    title = models.CharField(max_length=255)
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    audio = models.FileField(upload_to='audio/')
    cover = models.ImageField(upload_to='covers/')
    description = models.TextField(blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='track')
    likes_count = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, verbose_name='Причина отклонения')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_approved(self):
        return self.status == 'approved'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')