from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class DashboardStat(models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    tenant = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}: {self.value}"
