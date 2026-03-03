from rest_framework import serializers
from .models import Product, ProductCategory, SaveProducts


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


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