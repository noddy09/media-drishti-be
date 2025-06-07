from django.db import models
from django.contrib.auth import get_user_model
from backend.uploads.models import Upload

class Clip(models.Model):
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='clips')
    # Coordinates for the clip region (for images/PDFs)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='clips')
    created_at = models.DateTimeField(auto_now_add=True)
    tenant = models.CharField(max_length=100)

    def __str__(self):
        return f"Clip {self.id} on {self.upload}"
