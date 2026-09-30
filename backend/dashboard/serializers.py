from rest_framework import serializers
from .models import DashboardStat

class DashboardStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardStat
        fields = '__all__'
        read_only_fields = ('updated_at',)


class RecentActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.SerializerMethodField()
    action = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()

    def get_user(self, obj):
        return obj.user.username if obj.user else None

