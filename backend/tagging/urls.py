from rest_framework.routers import DefaultRouter
from .views import TagViewSet, ClipTagViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'clip-tags', ClipTagViewSet, basename='cliptag')

urlpatterns = router.urls
