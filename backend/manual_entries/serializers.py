from rest_framework import serializers
from .models import ManualEntry

class ManualEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualEntry
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')
