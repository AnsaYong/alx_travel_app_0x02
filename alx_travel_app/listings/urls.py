from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ListingViewSet, BookingViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"listings", ListingViewSet, basename="listings")
router.register(r"bookings", BookingViewSet, basename="bookings")

urls = router.urls

urlpatterns = [
    (path("", include(router.urls))),
]
