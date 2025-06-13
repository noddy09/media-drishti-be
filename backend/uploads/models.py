from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os
from datetime import datetime

class Upload(models.Model):
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('image', 'Image'),
    ]
    def upload_to_uuid(instance, filename):
        ext = filename.split('.')[-1]
        uuid_name = f"{uuid.uuid4()}.{ext}"
        now = datetime.now()
        return os.path.join('uploads', str(now.year), str(now.month).zfill(2), uuid_name)

    file = models.FileField(upload_to=upload_to_uuid)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, null=True, default="test")  # User-provided name

    def __str__(self):
        return f"{self.name or self.file.name} ({self.file_type})"
