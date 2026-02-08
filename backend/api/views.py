from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ContactMessage


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
def create_contact_message(request):
    name = str(request.data.get("name", "")).strip()
    email = str(request.data.get("email", "")).strip()
    message = str(request.data.get("message", "")).strip()

    if not name or not email or not message:
        return Response(
            {"detail": "Name, email, and message are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"detail": "Invalid email address."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    saved_message = ContactMessage.objects.create(
        name=name,
        email=email,
        message=message,
    )
    return Response(
        {"status": "received", "id": saved_message.id},
        status=status.HTTP_201_CREATED,
    )
