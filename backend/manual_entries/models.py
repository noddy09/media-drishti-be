from django.db import models
from django.contrib.auth import get_user_model

class ManualEntry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.CharField(max_length=255, blank=True)  # Comma-separated tags for simplicity
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='manual_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    tenant = models.CharField(max_length=100)

    def __str__(self):
        return self.title
