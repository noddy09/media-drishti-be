from django.db import models
from django.contrib.auth import get_user_model

class Upload(models.Model):
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('image', 'Image'),
    ]
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tenant = models.CharField(max_length=100)  # For multi-tenancy

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"
