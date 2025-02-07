import random
from django.core.management.base import BaseCommand
from listings.models import Listing


class Command(BaseCommand):
    help = "Seed the database with sample listing data"

    def handle(self, *args, **kwargs):
        # Clear existing data to avoid duplication (optional)
        Listing.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing listings."))

        # Sample data to populate the database
        titles = [
            "Cozy Apartment in the City Center",
            "Luxury Villa with Ocean View",
            "Modern Studio Near Downtown",
            "Spacious Country House",
            "Penthouse in High-Rise Building",
        ]
        descriptions = [
            "A beautiful and cozy place to stay.",
            "Amazing amenities and stunning views.",
            "Perfect for travelers and business trips.",
            "Quiet and serene environment.",
            "Luxury living at its finest.",
        ]
        prices = [99.99, 250.50, 150.00, 300.75, 500.00]

        # Generate 10 sample listings
        for _ in range(10):
            title = random.choice(titles)
            description = random.choice(descriptions)
            price = random.choice(prices)
            photo = "photos/sample.jpg"  # Update with a valid path to a sample photo

            listing = Listing.objects.create(
                title=title,
                description=description,
                price=price,
                photo=photo,
                is_published=random.choice([True, False]),
            )
            self.stdout.write(self.style.SUCCESS(f"Created listing: {listing.title}"))

        self.stdout.write(self.style.SUCCESS("Database seeded with sample listings."))
