from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from .managers import UserManager
import uuid

# User Model-----------
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150,null=True, blank=True)

    profile_picture = models.ImageField(upload_to="User/Profile_picture",blank=True, null=True)
    creator = models.BooleanField(default=False,null=True, blank=True)

    skin_tone = models.CharField(max_length=50, blank=True)
    undertone = models.CharField(max_length=50, blank=True)
     
    stripe_account_id = models.CharField(max_length=255, null=True, blank=True)

    google_id = models.CharField(max_length=255, blank=True, null=True)
    google_image_url = models.URLField(blank=True, null=True)

    apple_id = models.CharField(max_length=255, blank=True, null=True)
    apple_image_url = models.URLField(blank=True, null=True)

    is_terms_service = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email
    
    
    
    
#----- verification code model -----------#
class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    expires_at = models.DateTimeField()
    purpose = models.CharField(
        max_length=20,
        choices=(("verify", "verify"), ("reset", "reset"))
    )