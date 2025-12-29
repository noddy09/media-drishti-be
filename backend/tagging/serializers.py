from rest_framework import serializers
from .models import Tag, ClipTag, ClientTag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ClipTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClipTag
        fields = '__all__'

class ClientTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTag
        fields = '__all__'
