from django.db import models
from backend.uploads.models import Upload

# Create your models here.

class Download(models.Model):
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    downloaded_by = models.CharField(max_length=255)  # Could be user or client identifier
    tenant = models.CharField(max_length=100)

    def __str__(self):
        return f"Download of {self.upload} by {self.downloaded_by}"
