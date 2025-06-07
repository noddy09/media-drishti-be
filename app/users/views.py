from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import permissions, viewsets

from .serializers import UserSerializer

User = get_user_model()

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
