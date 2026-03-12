from rest_framework import serializers
from .models import LikedVideo, PrivacyPolicy, ProductReview, SavedVideo, SharedVideo, Video, VideoView
from Products.models import Order, OrderItem, Product, ProductCategory
from Products.serializers import ProductSerializer, productviewcartserializer



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
    user_name=serializers.CharField(source="user.full_name",read_only=True)
    class Meta:
        model = Video
        fields = ["id","user_name","caption", "product", "video_url",'like_count', 'share_count','saved_video',"created_at"]
        
        
#serializer for video upload and count view with product details
class VideoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoView
        fields = ["id", "video", "user", "viewed_at"]
        read_only_fields = ["id", "user", "viewed_at"]
        
        
#serializer for product review with user details   
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
    
    


# serializers for order and order item for show order history with product details
class OrderItemSerializer(serializers.ModelSerializer):
    product = productviewcartserializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id","quantity", 'price',"product"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount",  "delivery_method" 
                  , "created_at", "is_paid", "items"]
        read_only_fields = ["id", "status", "total_amount", "created_at", "is_paid"]
        
        
        
        
# commssion tracking serializer for creator to track their commission from product sales

class CommissionTrackingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    creator = serializers.CharField()
    date = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    # progress = serializers.CharField()
    
    
    
    
#serializer for admin added new policy for creator dashboard to show the policy details
class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = [
            "id",
            "title",
            "description",
            "created_at"
        ]
        
        
        
# saved Unsaved viddeo serializer for user
class VideoListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    creator_name = serializers.CharField(source="user.full_name", read_only=True)
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "video_url",
            "caption",
            "product_type",
            "shade",
            "product_name",
            "creator_name",
            "like_count",
            "share_count",
            "saved_video",
            "is_saved",
            "created_at",
        ]

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return SavedVideo.objects.filter(user=request.user, video=obj).exists()
        return False
        
        
        
        
class VideoListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    creator_name = serializers.CharField(source="user.full_name", read_only=True)
    is_saved = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "video_url",
            "caption",
            "product_type",
            "shade",
            "product_name",
            "creator_name",
            "like_count",
            "share_count",
            "saved_video",
            "is_saved",
            "is_liked",
            "created_at",
        ]

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return SavedVideo.objects.filter(user=request.user, video=obj).exists()
        return False

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return LikedVideo.objects.filter(user=request.user, video=obj).exists()
        return False
        
        
        
# Share video serializers for user to share the video with other user and also show the shared video list to userclass VideoListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    creator_name = serializers.CharField(source="user.full_name", read_only=True)
    is_saved = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "video_url",
            "caption",
            "product_type",
            "shade",
            "product_name",
            "creator_name",
            "like_count",
            "share_count",
            "saved_video",
            "is_saved",
            "is_liked",
            "is_shared",
            "created_at",
        ]

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return SavedVideo.objects.filter(user=request.user, video=obj).exists()
        return False

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return LikedVideo.objects.filter(user=request.user, video=obj).exists()
        return False

    def get_is_shared(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return SharedVideo.objects.filter(user=request.user, video=obj).exists()
        return False








# creator deshboard serializers
class ProductShownCreatorSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source="category.name", read_only=True)
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "shade",
            "price",
            "category",
            "colour_hex",
            "rating",
            "image",
            "created_at",
        ]
    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class CreatorVideoSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    creator_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "creator_name",
            "products",
            "like_count",
            "video_url",
            "created_at",
        ]

    def get_products(self, obj):
        products = Product.objects.filter(product_videos_product=obj)
        return ProductShownCreatorSerializer(products,many=True,context=self.context).data
    
    
    
from .models import SaveProduct

class ProductViewserializers(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'shade',
            'category',
            'colour_hex',
            'price',
            'discount_percentage',
            'rating',
            'description',
            'image',
            'created_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at']
        
class SaveProductSerializer(serializers.ModelSerializer):
    product=ProductViewserializers(read_only=True)
    class Meta:
        model = SaveProduct
        fields = ["id", "user", "product", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
        
        
        
        