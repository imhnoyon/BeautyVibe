from Products.models import Order, OrderItem
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import Video
from .serializers import *
from utils.api_response import APIResponse

class ProductCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = ProductCategory.objects.all().order_by("name")
        serializer = ProductCategorySerializer(categories, many=True)

        return APIResponse.success(
            message="Categories fetched successfully",
            data=serializer.data
        )
        
# show products by category       
from Products.pagination import CustomPagination
class ProductByCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, category_id):
        products = Product.objects.filter(
            category_id=category_id
        ).order_by("name")

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)

        return paginator.get_paginated_response({
            "message": "Products fetched successfully",
            "data": serializer.data
        })
        

# For video upload related to product
from django.shortcuts import get_object_or_404

class ProductVideoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
        
    def post(self, request, product_id):

        product = get_object_or_404(Product, id=product_id)

        serializer = ProductVideoSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save(
                product=product,
                user=request.user
            )
            user=request.user
            user.creator=True
            user.save()
            
            return APIResponse.success(
                message="Video uploaded successfully",
                data=serializer.data,
                status_code=201
            )
        return APIResponse.error(
            message="Invalid data provided",
            errors=serializer.errors
        )
        
        
class UserVideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.filter(user=request.user).order_by("-created_at")
        serializer = ProductVideoSerializer(videos, many=True , context={"request": request})

        return APIResponse.success(
            message="User videos fetched successfully",
            data=serializer.data
        )
        

#video watch view to register views for a video
class VideoWatchView(APIView):
    """
    POST /videos/watch/{video_id}/  -> register a view
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)

        # optional: prevent multiple views by same user in short time (not added now)
        VideoView.objects.create(video=video, user=request.user)

        total_views = VideoView.objects.filter(video=video).count()

        return APIResponse.success(
            message="View registered",
            data={"video_id": video.id, "views": total_views}
        )
        

from django.db.models import Count, Sum
from .models import Commission
class CreatorDashboardView(APIView):
    """
    GET /creator/dashboard/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        creator = request.user

        total_views = VideoView.objects.filter(video__user=creator).count()

        # Sales + commission (based on Commission table)
        agg = Commission.objects.filter(creator=creator).aggregate(
            total_sales=Sum("order_amount"),
            total_commission=Sum("commission_amount")
        )

        total_sales = agg["total_sales"] or 0
        total_commission = agg["total_commission"] or 0

        return APIResponse.success(
            message="Dashboard data fetched",
            data={
                "views": total_views,
                "sales": float(total_sales),
                "commission_earned": float(total_commission),
            }
        )
        
        

# review related views
class ProductReviewView(APIView):
    permission_classes = [IsAuthenticated]
    paginator_class = CustomPagination

    # ✅ list reviews of a product (paginated)
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        qs = ProductReview.objects.filter(product=product).select_related("user").order_by("-id")

        paginator = self.paginator_class()
        paginated = paginator.paginate_queryset(qs, request)

        serializer = ProductReviewSerializer(paginated, many=True)
        return paginator.get_paginated_response({
            "success": True,
            "message": "Reviews fetched successfully",
            "product_id": product.id,
            "product_name": product.name,
            "reviews": serializer.data
        })

    # ✅ create review for a product
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # ✅ Only buyers can review
        bought = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status="paid"
        ).exists()

        if not bought:
            return APIResponse.error(
                message="You must buy this product before reviewing.",
                status_code=403
            )

        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            review, created = ProductReview.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    "rating": serializer.validated_data["rating"],
                    "comment": serializer.validated_data.get("comment", "")
                }
            )

            data = ProductReviewSerializer(review).data
            return APIResponse.success(
                message="Review submitted successfully" if created else "Review updated successfully",
                data=data,
                status_code=201 if created else 200
            )

        return APIResponse.error(
            message="Invalid data",
            errors=serializer.errors,
            status_code=400
        )
        
        
        
        
        
class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    paginator_class = CustomPagination

    def get(self, request):
        qs = Order.objects.filter(user=request.user).prefetch_related("items").order_by("-created_at")

        paginator = self.paginator_class()
        paginated = paginator.paginate_queryset(qs, request)

        serializer = OrderSerializer(paginated, many=True, context={"request": request})
        return paginator.get_paginated_response({
            "success": True,
            "message": "Order history fetched successfully",
            "orders": serializer.data
        })