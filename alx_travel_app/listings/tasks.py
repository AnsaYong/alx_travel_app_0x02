from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_payment_confirmation_email(user_email, listing_title, transaction_id):
    subject = "Payment Confirmation"
    message = f"Your payment for the listing '{listing_title}' has been successfully processed.\nTransaction ID: {transaction_id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user_email])
