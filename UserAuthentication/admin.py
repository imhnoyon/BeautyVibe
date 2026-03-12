from django.contrib import admin
from .models import User, VerificationCode
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email','full_name','is_verified','is_staff','created_at')
    search_fields = ('email','full_name')
    
    
@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):  
    list_display = ('user','code','expires_at')
    # search_fields = ('user__email',)