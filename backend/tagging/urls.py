from rest_framework.routers import DefaultRouter
from .views import TagViewSet, ClipTagViewSet, ClientTagViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'clip-tags', ClipTagViewSet, basename='cliptag')
router.register(r'client-tags', ClientTagViewSet, basename='clienttag')

urlpatterns = router.urls
