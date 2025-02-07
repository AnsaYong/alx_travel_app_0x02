import requests
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_payment_confirmation_email

CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"


class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows listings to be viewed or edited.
    """

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """

    permission_classes = [AllowAny]

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    # @action(detail=True, methods=["post"], url_path="initiate-payment")
    # def initiate_payment(self, request, pk=None):
    #     booking = self.get_object()

    #     # Construct the payment initiation data
    #     payment_data = {
    #         "booking_id": booking.id,
    #     }

    #     # Send a POST request to the payment initiation endpoint
    #     response = requests.post(
    #         "http://localhost:8000/payments/initiate/",
    #         data=payment_data,
    #     )

    #     if response.status_code == 201:
    #         response_data = response.json()
    #         checkout_url = response_data.get("checkout_url")

    #         payment = Payment.objects.create(
    #             booking=booking,
    #             transaction_id=response_data["transaction_id"],
    #             amount=booking.listing.price,
    #             status="Pending",
    #         )

    #         return Response(
    #             {"message": "Payment initiated", "checkout_url": checkout_url},
    #             status=status.HTTP_201_CREATED,
    #         )

    #     return Response(
    #         {"error": "Failed to initiate payment", "details": response.json()},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )


class InitiatePaymentView(APIView):
    """Initiates a payment for a booking. It sends a request to the Chapa API with booking details."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")  # Booking ID from the request data
        booking = get_object_or_404(Booking, pk=booking_id)  # Verify booking existence

        # payload = {
        #     "amount": str(booking.listing.price),  # Chapa expects amount as a string
        #     "currency": "ETB",  # Ethiopian Birr
        #     # "email": booking.user.email,
        #     "first_name": booking.user.first_name,
        #     "last_name": booking.user.last_name,
        #     "phone_number": booking.user.profile.phone_number,
        #     "tx_ref": f"booking_{booking.id}-{booking.user.id}",  # Unique transaction reference
        #     # "callback_url": "https://exampledomain.com/payment/callback",
        #     # "return_url": "https://exampledomain.com/payment/success",
        #     "customizations": {
        #         "title": "Booking Payment",
        #         "description": f"Payment for booking {booking.listing.title}",
        #     },
        # }

        # Test data
        payload = {
            "amount": "500",  # Chapa expects amount as a string
            "currency": "ETB",  # Ethiopian Birr
            # "email": booking.user.email,
            "first_name": "Ansa",
            "last_name": "Nke",
            "phone_number": +27844437287,
            "tx_ref": f"booking_001-23",  # Unique transaction reference
            "customizations": {
                "title": "Booking Payment",
                "description": f"Payment for booking Test",
            },
        }
        transaction_id = payload[
            "tx_ref"
        ]  # Chapa doesn't seem to return a transaction ID
        amount = payload["amount"]

        # Send request to Chapa API
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.post(CHAPA_API_URL, json=payload, headers=headers)

        # Handle response from Chapa API
        if response.status_code == 200:
            response_data = response.json()
            checkout_url = response_data["data"].get(
                "checkout_url"
            )  # Chapa payment URL

            # Create a Payment record
            payment = Payment.objects.create(
                booking=booking,
                transaction_id=transaction_id,
                amount=amount,
                status="pending",
            )

            # Redirect the user to the checkout URL
            return Response(
                {"message": "Payment initiated", "checkout_url": checkout_url},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"error": "Failed to initiate payment", "details": response.json()},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyPaymentView(APIView):
    """
    Verifies the status of a payment with Chapa.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get("transaction_id")
        if not transaction_id:
            return Response(
                {"error": "Transaction ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve the payment record
        payment = get_object_or_404(Payment, transaction_id=transaction_id)

        # Send request to Chapa for verification
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        response = requests.get(f"{CHAPA_VERIFY_URL}{transaction_id}/", headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            status_code = response_data.get("status")
            chapa_status = response_data.get("data", {}).get("status", "").lower()

            print("Chapa status:", chapa_status)

            if chapa_status == "success":
                payment.status = "Completed"
                # Send confirmation email asynchronously using celery
                send_payment_confirmation_email.delay(
                    payment.booking.user.email,
                    payment.booking.listing.title,
                    payment.transaction_id,
                )
            elif chapa_status == "failed":
                payment.status = "Failed"
            else:
                payment.status = "Pending"
                print("Payment has been updated to pending")

            payment.save()

            return Response(
                {
                    "message": "Payment status updated",
                    "transaction_id": transaction_id,
                    "status": payment.status,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Failed to verify payment", "details": response.json()},
            status=status.HTTP_400_BAD_REQUEST,
        )
