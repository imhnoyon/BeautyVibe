from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'caption', 'product_type', 'shade',  'video_url', 'created_at')
    search_fields = ('user__username', 'product__name', 'caption', 'product_type', 'shade', 'product_tag')
    list_filter = ('created_at',)
    
    
    
@admin.register(VideoView)
class VideoViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user', 'viewed_at')
    search_fields = ('video__caption', 'user__username')
    list_filter = ('viewed_at',)
    
    
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'video', 'order_amount', 'commission_amount', 'created_at')
    search_fields = ('creator__username', 'video__caption')
    list_filter = ('created_at',)
    
    
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'comment', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    list_filter = ('created_at',)