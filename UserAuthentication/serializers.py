from Products.models import Order, OrderItem, Product
from rest_framework import serializers
from .models import User  

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repassword = serializers.CharField(write_only=True, min_length=8)
    is_terms_service = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'repassword', 'is_terms_service']

    def validate(self, attrs):
        if attrs['password'] != attrs['repassword']:
            raise serializers.ValidationError({"password": "Password fields do not match."})
        if not attrs.get('is_terms_service', False):
            raise serializers.ValidationError({"is_terms_service": "You must accept the terms and conditions."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('repassword')  # remove repassword

        user = User.objects.create_user(
            full_name=validated_data['full_name'],
            email=validated_data['email'],  # fixed
            password=validated_data['password'],
            is_terms_service=validated_data['is_terms_service'],
        )
        return user

#-------Google signin Serializer --------#
class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    
    
    
#---------profile image serializer---------#
class ProfileImageSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(use_url=True)
    class Meta:
        model = User
        fields = ['full_name','profile_picture', 'skin_tone', 'undertone', 'face_shape', 'eye_color','email', 'confidence_score', 'summary']
        
        
        
        
class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'colour_hex', 'category','colour_hex', 'price', 'description','image', 'created_at', 'updated_at']
        
        
        
        
        
from rest_framework import serializers
from Products.models import Product, ProductCategory


class AIUserProfileSerializer(serializers.Serializer):
    skin_tone = serializers.CharField(allow_blank=True, required=False)
    undertone = serializers.CharField(allow_blank=True, required=False)
    face_shape = serializers.CharField(allow_blank=True, required=False)
    eye_color = serializers.CharField(allow_blank=True, required=False)
    confidence_score = serializers.IntegerField(required=False)
    summary = serializers.CharField(allow_blank=True, required=False)


class AICategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug", "created_at", "updated_at"]


class AIProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "shade",
            "price",
            "discount_percentage",
            "rating",
            "image",
            "category",
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else ""

    def get_image(self, obj):
        request = self.context.get("request")
        image = getattr(obj, "image", None)
        if image:
            try:
                return request.build_absolute_uri(image.url) if request else image.url
            except Exception:
                return ""
        return ""

    def get_rating(self, obj):
        rating = getattr(obj, "rating", 0)
        return str(rating if rating is not None else 0)

    def get_discount_percentage(self, obj):
        discount = getattr(obj, "discount_percentage", 0)
        return discount if discount is not None else 0


class RecommendationPayloadSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    user_profile = ProfileImageSerializer()
    categories = AICategorySerializer(many=True)
    products = AIProductSerializer(many=True)


class ProductRecommendationSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "shade",
            "price",
            "discount_percentage",
            "rating",
            "image",
            "category",
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else ""

    def get_image(self, obj):
        request = self.context.get("request")
        image = getattr(obj, "image", None)
        if image:
            try:
                return request.build_absolute_uri(image.url) if request else image.url
            except Exception:
                return ""
        return ""
    
    
    
    



#admin dashboard serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    shade=serializers.CharField(source='product.shade', read_only=True)
    colour_hex=serializers.CharField(source='product.colour_hex', read_only=True)
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "product_image",
            "shade",
            "colour_hex",
            "quantity",
            "price"
        ]

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

    def get_product_image(self, obj):
        request = self.context.get("request")
        if obj.product and obj.product.image:
            if request:
                return request.build_absolute_uri(obj.product.image.url)
            return obj.product.image.url
        return None
    
    
    
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "mobile_number",
            "emirate",
            "area",
            "building_name",
            "apartment_no",
            "total_amount",
            "status",
            "is_paid",
            "created_at",
            "items"
        ]
        
        
        
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone


class UserDetailSerializer(serializers.ModelSerializer):
    total_spending = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()
    current_orders = serializers.SerializerMethodField()
    previous_orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "profile_picture",
            "created_at",
            "total_spending",
            "total_orders",
            "current_orders",
            "previous_orders",
        ]

    def get_total_spending(self, obj):
        total = obj.orders.filter(is_paid=True).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        return float(total)

    def get_total_orders(self, obj):
        return obj.orders.count()

    def get_current_orders(self, obj):
        two_days_ago = timezone.now() - timedelta(days=2)

        orders = obj.orders.filter(
            created_at__gte=two_days_ago
        ).prefetch_related("items__product").order_by("-created_at")

        return OrderSerializer(
            orders,
            many=True,
            context=self.context
        ).data

    def get_previous_orders(self, obj):
        two_days_ago = timezone.now() - timedelta(days=2)

        orders = obj.orders.filter(
            created_at__lt=two_days_ago
        ).prefetch_related("items__product").order_by("-created_at")

        return OrderSerializer(
            orders,
            many=True,
            context=self.context
        ).data
        
        
        
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "creator",
            "profile_picture",
            "created_at"
        ]