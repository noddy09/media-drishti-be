from django.db import models
from django.contrib.auth import get_user_model

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('upload', 'Upload'),
        ('clip', 'Clip'),
        ('tag', 'Tag'),
        ('manual_entry', 'Manual Entry'),
        ('download', 'Download'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tenant = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"
