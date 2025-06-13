from django.db import models
from backend.clipping.models import Clip

class Tag(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class ClipTag(models.Model):
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE, related_name='clip_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='clip_tags')
    def __str__(self):
        return f"{self.clip} - {self.tag}"
