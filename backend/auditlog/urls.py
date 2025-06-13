from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet

router = DefaultRouter()
router.register(r'auditlog', AuditLogViewSet, basename='auditlog')

urlpatterns = router.urls