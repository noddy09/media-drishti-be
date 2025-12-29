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

class ClientTag(models.Model):
    client = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='client_tags', limit_choices_to={'is_staff': False, 'is_superuser': False})
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='client_tags')
    
    class Meta:
        unique_together = ('client', 'tag')
    
    def __str__(self):
        return f"{self.client.username} - {self.tag.name}"
