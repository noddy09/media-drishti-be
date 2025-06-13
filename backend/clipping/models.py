from django.db import models
from django.contrib.auth import get_user_model
from backend.uploads.models import Upload

class Clip(models.Model):
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='clips')
    # Coordinates for the clip region (for images/PDFs)
    x = models.FloatField()
    y = models.FloatField()
    width = models.IntegerField()
    height = models.IntegerField()
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='clips')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Clip {self.id} on {self.upload}"
