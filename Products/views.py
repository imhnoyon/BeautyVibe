from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import *
from .models import *
from utils.api_response import APIResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .pagination import CustomPagination

# create product and list all products or retrieve single product also delete product
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    paginator_class =CustomPagination
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
        
        # ✅ Apply Pagination
        paginator = self.paginator_class()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True, context={'request': request})
        
        return APIResponse.success(
            message="Product list retrieved successfully",
            data={
                "total": products.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "products": serializer.data
            }
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




# Explore view with category filter and search Functionality
class ExploreView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    def get(self, request):
        category_slug = request.query_params.get('category')
        search_query = request.query_params.get('search')
        categories = ProductCategory.objects.all()
        category_serializer = ProductCategorySerializer(categories, many=True)
        products = Product.objects.all()
        if category_slug:
            products = products.filter(category__slug=category_slug)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
            
        total_products = products.count()
        # ✅ Apply Pagination ONLY to products
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)

        product_serializer = ProductListSerializer(
            paginated_products,
            many=True,
            context={'request': request}
        )
        # product_serializer = ProductListSerializer(products, many=True, context={'request': request})

        return APIResponse.success(
            message="Explore data retrieved successfully",
            data={
                "categories": category_serializer.data,
                "total_products": total_products,
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "products": product_serializer.data
            },
            status_code=status.HTTP_200_OK
        )

# Product details view with 
class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, context={'request': request})
        
        return APIResponse.success(
            message="Product detail retrieved successfully",
            data=serializer.data
        )

#save product view for user to save products to their profile
class SaveProductsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    # GET → List all saved products of user
    def get(self, request):
        saved_products = SaveProducts.objects.filter(
            user=request.user
        ).select_related('product')
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(saved_products, request)
        serializer = SavedProductSerializer(page, many=True, context={'request':request})

        return APIResponse.success(
            message="Saved products fetched successfully",
            data={
                "total": saved_products.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "products": serializer.data
            },
            status_code=status.HTTP_200_OK
        )
    def post(self, request):
        serializer = SavedProductSerializer(data=request.data,context={'request':request})

        if serializer.is_valid():
            product = serializer.validated_data['product']
            shade = serializer.validated_data.get('shade')
            colour_hex = serializer.validated_data.get('colour_hex')

            saved_product, created = SaveProducts.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={
                    'shade': shade,
                    'colour_hex': colour_hex
                }
            )

            if created:
                message = "Product Saved Successfully"
                status_code = status.HTTP_201_CREATED
            else:
                message = "Product Already Saved"
                status_code = status.HTTP_200_OK

            return APIResponse.success(
                message=message,
                data=SavedProductSerializer(saved_product).data,
                status_code=status_code
            )

        return APIResponse.error(
            message="Invalid data",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        
        

# save product delete view for user to delete saved products from their profile
class DeleteSaveProductsView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        try:
            delete_product = SaveProducts.objects.get(
                id=pk,
                user=request.user
            )
        except SaveProducts.DoesNotExist:
            return APIResponse.error(
                message='Save product not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

        delete_product.delete()

        return APIResponse.success(
            message= 'Save product deleted successfully',
            status_code=status.HTTP_200_OK
        )