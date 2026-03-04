from rest_framework import serializers
from .models import Video
from Products.models import Product, ProductCategory
from Products.serializers import ProductSerializer

class VideoUploadSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    name = serializers.CharField(write_only=True)
    category = serializers.CharField(write_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    caption = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Video
        fields = [
            'id', 'user', 'product', 'product_details', 
            'name', 'category', 'shade', 'product_tag', 
            'price', 'video_url', 'caption', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'product', 'created_at', 'updated_at']

    def create(self, validated_data):
        try:
            name = validated_data.pop('name', '').strip()
            category_name = validated_data.pop('category', '').strip()
            price = validated_data.pop('price', 0)
            shade = validated_data.get('shade', '').strip()
            caption = validated_data.pop('caption', None) # Pop caption, default to None if not provided
            user = self.context['request'].user

            if not name or not category_name:
                raise serializers.ValidationError("Product name and category are required")

            if not caption: # If caption was not provided or was empty, default to product name
                caption = name

            print(f"DEBUG: Processing upload for '{name}' in '{category_name}'")

            # 1. Get or Create Category
            category, _ = ProductCategory.objects.get_or_create(name=category_name)

            # 2. Get or Create Product (Handling duplicates safely)
            product = Product.objects.filter(name=name, shade=shade).first()
            
            if not product:
                product = Product.objects.create(
                    name=name,
                    shade=shade,
                    category=category,
                    price=price,
                    brand='BeautyVibe',
                    description=f"Added via video upload"
                )
                print(f"DEBUG: Created new product ID {product.id}")
            else:
                # If product existed but category was different or missing, update it
                if not product.category or product.category != category:
                    product.category = category
                    product.save()
                print(f"DEBUG: Found existing product ID {product.id}")

            print(f"DEBUG: Using Product ID {product.id}")

            # 3. Create Video linked to this product
            video = Video.objects.create(
                user=user,
                product=product,
                product_type=category_name,
                caption=caption,
                **validated_data
            )

            # Update creator status
            if not user.creator:
                user.creator = True
                user.save(update_fields=['creator'])

            return video
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise serializers.ValidationError(str(e))
