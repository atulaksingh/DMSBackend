from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from rest_framework.views import exception_handler
from django.db import IntegrityError
from rest_framework.response import Response

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_active))
generate_token=TokenGenerator()

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, IntegrityError):
        error_message = str(exc)

        # Check if it's the specific UNIQUE constraint for client+email
        if "api_commonuser.client_id, api_commonuser.email" in error_message:
            return Response(
                {"error_message": "A user with this email already exists."},
                status=400
            )

        # Fallback for other IntegrityErrors
        return Response(
            {"error_message": "Database integrity error."},
            status=400
        )

    return response
