from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ListingViewSet,
    BookingViewSet,
    PaymentViewSet,
    InitiatePaymentView,
    VerifyPaymentView,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"listings", ListingViewSet, basename="listings")
router.register(r"bookings", BookingViewSet, basename="bookings")
router.register(r"payments", PaymentViewSet, basename="payments")

urls = router.urls

urlpatterns = [
    (path("", include(router.urls))),
    path("payments/initiate/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("payments/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
]
