from rest_framework import serializers
from .models import ProductReview, Video, VideoView
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
        
#serializer for video upload and count view with product details
class VideoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoView
        fields = ["id", "video", "user", "viewed_at"]
        read_only_fields = ["id", "user", "viewed_at"]
        
        
class ProductReviewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ProductReview
        fields = ["id", "user", "full_name", "product", "rating", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "product", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value