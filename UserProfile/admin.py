from django.contrib import admin
from .models import Video
# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'caption', 'product_type', 'shade',  'video_url', 'created_at')
    search_fields = ('user__username', 'product__name', 'caption', 'product_type', 'shade', 'product_tag')
    list_filter = ('created_at',)