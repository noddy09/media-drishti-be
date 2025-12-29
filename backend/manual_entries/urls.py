from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManualEntryViewSet

router = DefaultRouter()
# Register at root so the app prefix provides the full path `/api/manual-entries/`
router.register(r'', ManualEntryViewSet, basename='manualentry')

urlpatterns = [
	path('', include(router.urls)),
]
