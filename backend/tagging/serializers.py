from rest_framework import serializers
from .models import Tag, ClipTag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ClipTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClipTag
        fields = '__all__'
