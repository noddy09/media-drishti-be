from rest_framework import serializers
from .models import ManualEntry
from backend.tagging.models import Tag

class ManualEntrySerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    
    class Meta:
        model = ManualEntry
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        entry = super().create(validated_data)
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            entry.tags.add(tag)
        return entry
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance
