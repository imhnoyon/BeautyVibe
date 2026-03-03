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
