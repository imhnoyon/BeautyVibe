from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import *
from .models import Product,ProductCategory
from utils.api_response import APIResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q


class ExploreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_slug = request.query_params.get('category')
        search_query = request.query_params.get('search')

        # Get all categories for the horizontal list
        categories = ProductCategory.objects.all()
        category_serializer = ProductCategorySerializer(categories, many=True)

        # Start with all products
        products = Product.objects.all()

        # Filter by category if provided
        if category_slug:
            products = products.filter(category__slug=category_slug)

        # Filter by search query if provided
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        product_serializer = ProductListSerializer(products, many=True, context={'request': request})

        return APIResponse.success(
            message="Explore data retrieved successfully",
            data={
                "categories": category_serializer.data,
                "products": product_serializer.data
            }
        )



# create product and list all products or retrieve single product also delete product
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            product = serializer.save()
            return APIResponse.success(
                message="Product created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Failed to create product",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
    # 🔹 LIST ALL PRODUCTS OR RETRIEVE SINGLE PRODUCT
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return APIResponse.success(
                message="Product retrieved successfully",
                data=serializer.data
            )

        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return APIResponse.success(
            message="Product list retrieved successfully",
            data=serializer.data
        )
        
    # 🔹 DELETE PRODUCT
    def delete(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return APIResponse.success(
            message="Product deleted successfully",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT
        )

# list products by category slug
class SingleCategoryProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        category = ProductCategory.objects.get(slug=slug)
        products = category.products.all()
        serializer = ProductListSerializer(products, many=True)

        return APIResponse.success(
            message="Category products",
            data={
                "category": category.name,
                "products": serializer.data
            }
        )
