from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ('name', 'slug')
    list_filter = ('slug', 'created_at')
    ordering = ('created_at',)
    
    
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "shade", "brand", "category", "colour_hex", "price")
    search_fields = ('name', 'brand', 'slug')
    list_filter = ('slug','brand' , 'category')
    ordering = ('created_at',)

# @admin.register(SavedProduct)
# class SavedProductAdmin(admin.ModelAdmin):
#     list_display = ("user", "product", "saved_at")
#     search_fields = ('user__username', 'product__name')
#     list_filter = ('saved_at',)
#     ordering = ('saved_at',)
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ('user__username',) 
    list_filter = ('created_at', 'updated_at')
    ordering = ('created_at',)
    
@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "created_at")
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('created_at',)
    ordering = ('created_at',)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "total_amount", "status", "created_at")
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')
    ordering = ('created_at',)
    
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "caption", "created_at")
    search_fields = ('user__username', 'product__name', 'caption')
    list_filter = ('created_at',)
    ordering = ('created_at',)
    
