# serializers.py
from Products.serializers import ProductCategorySerializer, ProductSerializer
from rest_framework import serializers
from Products.models import ProductCategory, Video, Product



#Video Upload Serializer
class VideoUploadSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'user',
            'product',
            'product_details',
            'caption',
            'product_type',
            'shade',
            'product_tag',
            'video_url',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'video_url', 'user', 'product']

    def validate(self, attrs):
        product_type = attrs.get("product_type")
        shade = attrs.get("shade")

        try:
            product = Product.objects.get(name=product_type, shade=shade)
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'No product found with given product_type and shade'
            })

        attrs['product_instance'] = product
        return attrs

    def create(self, validated_data):
        product = validated_data.pop('product_instance')
        user = self.context['request'].user

        video = Video.objects.create(
            user=user,
            product=product,
            **validated_data
        )

        if not user.creator:
            user.creator = True
            user.save(update_fields=['creator'])

        return video

    def get_product_details(self, obj):
        return ProductSerializer(obj.product).data
    
    




