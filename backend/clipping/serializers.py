from rest_framework import serializers
from .models import Clip
from backend.tagging.models import Tag, ClipTag
from backend.tagging.serializers import TagSerializer

class ClipSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    class Meta:
        model = Clip
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')

    def validate(self, data):
        # Ensure x, y, width, height are integers
        for field in ['x', 'y', 'width', 'height']:
            if field in data and not isinstance(data[field], (int, float)):
                try:
                    data[field] = int(data[field])
                except Exception:
                    raise serializers.ValidationError({field: 'A valid integer is required.'})
        # Remove tenant requirement
        data.pop('tenant', None)
        # Accept 'upload' as either pk or object
        if 'upload' not in data:
            raise serializers.ValidationError({'upload': 'This field is required.'})
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        clip = super().create(validated_data)
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            ClipTag.objects.create(clip=clip, tag=tag)
        return clip
