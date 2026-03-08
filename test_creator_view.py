import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BeautyVibe.settings')
django.setup()

from django.conf import settings
settings.DEBUG_PROPAGATE_EXCEPTIONS = True

from rest_framework.test import APIClient
from UserAuthentication.models import User

user_id = '50d02fa6-2999-4f8a-ad2d-676a392186c0'
try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    user = User.objects.first()

client = APIClient()
client.force_authenticate(user=user)

try:
    response = client.get(f'/api/v1/auth/users-creators/{user_id}/')
    if response.status_code == 404:
        response = client.get(f'/auth/users-creators/{user_id}/')
    print('status_code=', response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
