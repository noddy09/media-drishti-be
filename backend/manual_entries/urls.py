from rest_framework.routers import DefaultRouter
from .views import ManualEntryViewSet

router = DefaultRouter()
router.register(r'manual-entries', ManualEntryViewSet, basename='manualentry')

urlpatterns = router.urls
