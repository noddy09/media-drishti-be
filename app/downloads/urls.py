from rest_framework.routers import DefaultRouter
from .views import DownloadViewSet

router = DefaultRouter()
router.register(r'downloads', DownloadViewSet, basename='download')

urlpatterns = router.urls
