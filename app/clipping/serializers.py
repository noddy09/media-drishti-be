from rest_framework import serializers
from .models import Clip

class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')
