from UserAuthentication.models import User
from rest_framework import serializers
from .models import PaymentHistory, Product, ProductCategory, SaveProducts, Cart, CartItems, Order, OrderItem
from Products.models import CreatorWithdrawal

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']




# product serializer for create and update product
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=ProductCategory.objects.all(),
        slug_field='name'   
    )
    image = serializers.ImageField(required=False)
     

    class Meta:
        model = Product
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
        

        
        
        
# Slug based filter product category
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'shade',
            'price',
            'discount_percentage',
            'rating',
            'image'
        ]


class CategoryWithProductsSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'name',
            'slug',
            'products'
        ]
        
        
        
#Savedproduct model serializers----
class SavedProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = SaveProducts
        fields = [
            "id",
            "user",
            "product",
            "product_id",
            "shade",
            "colour_hex",
            "saved_at"
        ]

        read_only_fields = ["id","saved_at","user","product"]


#unkhown serializers  not working right now
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'colour_hex', 'shade', 'image']


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'shade', 'category_name', 
            'colour_hex', 'price', 'discount_percentage', 
            'rating', 'description', 'image', 'variants', 'created_at'
        ]

    def get_variants(self, obj):
        # Return other products that share the same name and brand (different shades)
        variants = Product.objects.filter(name=obj.name, brand=obj.brand).exclude(id=obj.id)
        return ProductVariantSerializer(variants, many=True, context=self.context).data



class productviewcartserializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'shade', 'colour_hex', 'price', 'discount_percentage', 'image']

#Cart Serializers
class CartItemSerializer(serializers.ModelSerializer):
    product_details = productviewcartserializer(source='product', read_only=True)
    
    class Meta:
        model = CartItems
        fields = [
            'id', 'product', 'video', 'shade', 
            'colour_hex', 'quantity', 'product_amount', 'product_details','created_at'
        ]
        read_only_fields = ['id', 'product_amount', 'created_at']

    def validate(self, data):
        if not data.get('product'):
            raise serializers.ValidationError("Product is required")
        return data


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return sum(item.product_amount for item in obj.cart_items.all())


# --- Order Serializers ---

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = productviewcartserializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'video', 'shade', 'colour_hex', 
            'quantity', 'price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'full_name', 'mobile_number', 'emirate', 
            'area', 'building_name', 'apartment_no', 'landmark', 
            'delivery_method', 'delivery_charge', 'delivery_note', 
            'total_amount', 'status', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'total_amount', 'status', 'created_at']
        
        
        
# AI product recommendation serializer
class ProductRecommendationSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=ProductCategory.objects.all(), slug_field='name')
    # image = serializers.ImageField(required=False)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            # 'slug',
            'brand',
            'shade',
            'category',
            'colour_hex',
            'price',
            # 'discount_percentage',
            # 'rating',
            'description',
            # 'image',
            # 'created_at',
        ]
        read_only_fields = ['id']


class UserProfileAIRecSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['skin_tone', 'undertone', 'face_shape', 'eye_color', 'confidence_score', 'summary']
        


class RecommendationResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField(source='id')  
    user_profile = UserProfileAIRecSerializer(read_only=True)  
    products = ProductRecommendationSerializer(many=True)

    
    
    


#product category serializer for create and update category
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]
        
        
        
        
#admin deshboard serializer 
class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'full_name', 'mobile_number', 'emirate', 
            'area', 'building_name', 'apartment_no', 'landmark', 
            'delivery_method', 'delivery_charge', 'delivery_note', 
            'total_amount','number_of_items', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'total_amount', 'status', 'created_at']
        
        
#payment history serializer for admin dashboard       
class PaymentHistorySerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="user.full_name")

    class Meta:
        model = PaymentHistory
        fields = [
            "payment_id",
            "customer",
            "created_at",
            "amount",
            "transaction_method"
        ]
        
        
#Withdraw history for creator-profile
class WithdrawHistorySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    withdraw_date = serializers.DateTimeField(source="requested_at", format="%b %d, %Y", read_only=True)

    class Meta:
        model = CreatorWithdrawal
        fields = [
            "id",
            "withdraw_id",
            "title",
            "amount",
            "status",
            "bank_name",
            "bank_last4",
            "withdraw_method",
            "withdraw_date",
            "requested_at",
        ]

    def get_title(self, obj):
        if obj.bank_name and obj.bank_last4:
            return f"Payout to {obj.bank_name} ••{obj.bank_last4}"
        return "Withdraw Request"