from rest_framework import serializers
from .models import Video, VideoView
from Products.models import Product, ProductCategory
from Products.serializers import ProductSerializer

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug"]
        
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "category", "brand", "shade", "colour_hex", "price", "discount_percentage", "slug"]
        
#added video upload serializer for product 
class ProductVideoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Video
        fields = ["id", "product", "video_url", "created_at"]
        
        
class VideoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoView
        fields = ["id", "video", "user", "viewed_at"]
        read_only_fields = ["id", "user", "viewed_at"]