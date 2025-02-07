from rest_framework import serializers
from .models import Listing, Booking
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = "__all__"  # Include all fields of the model
        read_only_fields = ["list_date"]  # Optional: Make 'list_date' read-only


class BookingSerializer(serializers.ModelSerializer):
    # Nested representation of the listing
    listing = ListingSerializer(read_only=True)
    # Only include the ID for the listing when creating or updating
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source="listing", write_only=True
    )

    # Nested representation of the user
    user = serializers.StringRelatedField(read_only=True)
    # Only include the ID for the user when creating or updating
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["booking_date"]
