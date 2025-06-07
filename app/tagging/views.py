from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Tag, ClipTag
from .serializers import TagSerializer, ClipTagSerializer

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClipTagViewSet(viewsets.ModelViewSet):
    queryset = ClipTag.objects.all()
    serializer_class = ClipTagSerializer
    permission_classes = [permissions.IsAuthenticated]
