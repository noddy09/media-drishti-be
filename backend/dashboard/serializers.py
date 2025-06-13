from rest_framework import serializers
from .models import DashboardStat

class DashboardStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardStat
        fields = '__all__'
        read_only_fields = ('updated_at',)
