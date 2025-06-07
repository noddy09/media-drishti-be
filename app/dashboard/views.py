from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import DashboardStat
from .serializers import DashboardStatSerializer

# Create your views here.

class DashboardStatViewSet(viewsets.ModelViewSet):
    queryset = DashboardStat.objects.all()
    serializer_class = DashboardStatSerializer
    permission_classes = [permissions.IsAuthenticated]
