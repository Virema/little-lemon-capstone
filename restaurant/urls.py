from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, MenuViewSet

router = DefaultRouter()
router.register("menu", MenuViewSet)
router.register("booking/tables", BookingViewSet)
urlpatterns = router.urls
