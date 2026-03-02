import random
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

def generate_otp():
    return str(random.randint(1000, 9999))

def otp_expiry(minutes=10):
    return timezone.now() + timedelta(minutes=minutes)

def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "access_token_valid_till": int(
            (timezone.now() + timedelta(minutes=30)).timestamp() * 1000
        ),
        "refresh_token": str(refresh),
    }