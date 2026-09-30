from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DashboardStatViewSet, RecentActivityView

router = DefaultRouter()
router.register(r'dashboard-stats', DashboardStatViewSet, basename='dashboardstat')

urlpatterns = router.urls + [
    path('recent-activity/', RecentActivityView.as_view(), name='recent-activity'),
]
