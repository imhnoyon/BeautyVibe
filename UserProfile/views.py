from Products.models import Order, OrderItem
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import *
from .serializers import *
from utils.api_response import APIResponse
from django.db.models import Q, Sum, Max
from django.shortcuts import get_object_or_404
from permission_class import IsCreator


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
        videos = Video.objects.order_by("-created_at")
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
        


# from django.db.models import Sum

class CreatorDashboardView(APIView):
    """
    GET /creator/dashboard/
    """
    permission_classes = [IsAuthenticated, IsCreator]
    pagination_class = CustomPagination

    def get(self, request):
        creator = request.user

        # total views
        total_views = VideoView.objects.filter(video__user=creator).count()

        # creator videos queryset
        videos = Video.objects.filter(user=creator).order_by("-created_at")
        total_videos = videos.count()

        # pagination apply only for videos
        paginator = self.pagination_class()
        paginated_videos = paginator.paginate_queryset(videos, request)

        video_serializer = CreatorVideoSerializer(
            paginated_videos,
            many=True,
            context={"request": request}
        )

        # Sales + commission
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
                "videos_count": total_videos,
                "commission_earned": float(total_commission),

                  # pagination outside
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),

                # videos list
                "videos": video_serializer.data
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
        
        
        
        
from permission_class import IsCreator
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
        
from Products.models import CreatorWithdrawal
# class CommissionTrackingAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination

#     def get(self, request):
#         search = request.query_params.get("search")

#         commissions = Commission.objects.select_related("creator", "video").all()

#         if search:
#             commissions = commissions.filter(
#                 Q(creator__full_name__icontains=search) |
#                 Q(creator__email__icontains=search)
#             )

#         grouped_commissions = (
#             commissions
#             .values("creator", "creator__full_name")
#             .annotate(
#                 total_sales=Sum("order_amount"),
#                 commission=Sum("commission_amount"),
#                 last_date=Max("created_at")
#             )
#             .order_by("-last_date")
#         )

#         commission_data = [
#             {
#                 "creator": item["creator__full_name"],
#                 "date": item["last_date"].strftime("%b %d, %Y") if item["last_date"] else None,
#                 "total_sales": item["total_sales"] or 0,
#                 "commission": item["commission"] or 0,
#                 "progress": "Paid" if (item["commission"] or 0) > 0 else "Pending",
#             }
#             for item in grouped_commissions
#         ]

#         # Top cards summary
#         total_withdraw = 0
#         paid_payouts = 0

#         for item in commission_data:
#             if item["progress"] == "Paid":
#                 paid_payouts += item["commission"]
#             else:
#                 pending_payouts += item["commission"]
                
#         # total withdrawn from withdrawal table
#         total_withdraw = CreatorWithdrawal.objects.filter(
#             status="completed"
#         ).aggregate(
#             total=Sum("amount")
#         )["total"] or 0
#         paginator = self.pagination_class()
#         paginated_data = paginator.paginate_queryset(commission_data, request)

#         serializer = CommissionTrackingSerializer(paginated_data, many=True)

#         return APIResponse.success(
#             message="Commission tracking retrieved successfully",
#             data={
#                 "summary": {
#                     "pending_payouts": paid_payouts,
#                     "total_withdraw": total_withdraw,
#                 },
#                 "table": {
#                     "total": len(commission_data),
#                     "page": paginator.page.number,
#                     "total_pages": paginator.page.paginator.num_pages,
#                     "next": paginator.get_next_link(),
#                     "previous": paginator.get_previous_link(),
#                     "commissions": serializer.data
#                 }
#             }
#         )
        

from django.db.models import Sum, Max, Q
from decimal import Decimal

class CommissionTrackingAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        search = request.query_params.get("search")

        commissions = Commission.objects.select_related("creator", "video").all()

        if search:
            commissions = commissions.filter(
                Q(creator__full_name__icontains=search) |
                Q(creator__email__icontains=search)
            )

        grouped_commissions = (
            commissions
            .values("creator", "creator__full_name")
            .annotate(
                total_sales=Sum("order_amount"),
                commission=Sum("commission_amount"),
                last_date=Max("created_at")
            )
            .order_by("-last_date")
        )

        commission_data = [
            {
                "creator": item["creator__full_name"],
                "date": item["last_date"].strftime("%b %d, %Y") if item["last_date"] else None,
                "total_sales": item["total_sales"] or 0,
                "commission": item["commission"] or 0,
            }
            for item in grouped_commissions
        ]

        # -------- SUMMARY --------

        total_commission = Commission.objects.aggregate(
            total=Sum("commission_amount")
        )["total"] or Decimal("0.00")

        total_withdraw = CreatorWithdrawal.objects.filter(
            status="completed"
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        pending_payouts = total_commission - total_withdraw

        # -------- PAGINATION --------

        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(commission_data, request)

        serializer = CommissionTrackingSerializer(paginated_data, many=True)

        return APIResponse.success(
            message="Commission tracking retrieved successfully",
            data={
                "summary": {
                    "pending_payouts": float(pending_payouts),
                    "total_withdraw": float(total_withdraw),
                },
                "table": {
                    "total": len(commission_data),
                    "page": paginator.page.number,
                    "total_pages": paginator.page.paginator.num_pages,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "commissions": serializer.data
                }
            }
        )
        

# admin can add new policy for creator 
class PrivacyPolicyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            policy = get_object_or_404(PrivacyPolicy, id=pk)
            serializer = PrivacyPolicySerializer(policy)
            return APIResponse.success(
                message="Policy retrieved successfully",
                data=serializer.data
            )

        policies = PrivacyPolicy.objects.all().order_by("-created_at")
        serializer = PrivacyPolicySerializer(policies, many=True)

        return APIResponse.success(
            message="Policy list retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = PrivacyPolicySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return APIResponse.success(
                message="Policy created successfully",
                data=serializer.data,
                status_code=201
            )

        return APIResponse.error(
            message="Failed to create policy",
            errors=serializer.errors
        )

    def put(self, request, pk):
        policy = get_object_or_404(PrivacyPolicy, id=pk)

        serializer = PrivacyPolicySerializer(
            policy,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return APIResponse.success(
                message="Policy updated successfully",
                data=serializer.data
            )

        return APIResponse.error(
            message="Failed to update policy",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        policy = get_object_or_404(PrivacyPolicy, id=pk)
        policy.delete()

        return APIResponse.success(
            message="Policy deleted successfully"
        )
        
        
        
# view to show saved videos for user

class SaveUnsaveVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)

        saved_obj = SavedVideo.objects.filter(user=request.user, video=video).first()

        if saved_obj:
            saved_obj.delete()

            if video.saved_video > 0:
                video.saved_video -= 1
                video.save(update_fields=["saved_video"])

            return APIResponse.success(
                message="Video unsaved successfully",
                data={
                    "video_id": video.id,
                    "is_saved": False,
                    "saved_count": video.saved_video
                }
            )

        SavedVideo.objects.create(user=request.user, video=video)
        video.saved_video += 1
        video.save(update_fields=["saved_video"])

        return APIResponse.success(
            message="Video saved successfully",
            data={
                "video_id": video.id,
                "is_saved": True,
                "saved_count": video.saved_video
            }
        )
        
        
        
# saved videos list for user
class SavedVideoListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        saved_videos = SavedVideo.objects.filter(
            user=request.user
        ).select_related(
            "video__product",
            "video__user"
        ).order_by("-created_at")

        videos = [item.video for item in saved_videos]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(videos, request)

        serializer = VideoListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return APIResponse.success(
            message="Saved video list retrieved successfully",
            data={
                "total": saved_videos.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "videos": serializer.data
            }
        )
        
        
        
        
# Video like unlike view for user to like and unlike the video
class LikeUnlikeVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)

        liked_obj = LikedVideo.objects.filter(user=request.user, video=video).first()

        if liked_obj:
            liked_obj.delete()

            if video.like_count > 0:
                video.like_count -= 1
                video.save(update_fields=["like_count"])

            return APIResponse.success(
                message="Video unliked successfully",
                data={
                    "video_id": video.id,
                    "is_liked": False,
                    "like_count": video.like_count
                }
            )

        LikedVideo.objects.create(user=request.user, video=video)
        video.like_count += 1
        video.save(update_fields=["like_count"])

        return APIResponse.success(
            message="Video liked successfully",
            data={
                "video_id": video.id,
                "is_liked": True,
                "like_count": video.like_count
            }
        )
        
        
        
# Liked videos list for user to see the liked videos and also remove the liked video from the list     
class LikedVideoListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        liked_videos = LikedVideo.objects.filter(
            user=request.user
        ).select_related(
            "video__product",
            "video__user"
        ).order_by("-created_at")

        videos = [item.video for item in liked_videos]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(videos, request)

        serializer = VideoListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return APIResponse.success(
            message="Liked video list retrieved successfully",
            data={
                "total": liked_videos.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "videos": serializer.data
            }
        )
        
        
# Share video view 
class ShareVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)

        SharedVideo.objects.create(
            user=request.user,
            video=video
        )

        video.share_count += 1
        video.save(update_fields=["share_count"])

        return APIResponse.success(
            message="Video shared successfully",
            data={
                "video_id": video.id,
                "share_count": video.share_count
            }
        )
        
        
        
class SharedVideoListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        shared_videos = SharedVideo.objects.filter(
            user=request.user
        ).select_related(
            "video__product",
            "video__user"
        ).order_by("-created_at")

        unique_videos = []
        seen_video_ids = set()

        for item in shared_videos:
            if item.video_id not in seen_video_ids:
                unique_videos.append(item.video)
                seen_video_ids.add(item.video_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(unique_videos, request)

        serializer = VideoListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return APIResponse.success(
            message="Shared video list retrieved successfully",
            data={
                "total": len(unique_videos),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "videos": serializer.data
            }
        )
        
        
#product save/Unsaved         
class SaveUnsaveProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        saved_product = SaveProduct.objects.filter(
            user=request.user,
            product=product
        ).first()

        if saved_product:
            saved_product.delete()
            return APIResponse.success(
                message="Product unsaved successfully",
                data={
                    "is_saved": False,
                    "product_id": product.id
                },
                status_code=200
            )

        saved_product = SaveProduct.objects.create(
            user=request.user,
            product=product
        )

        return APIResponse.success(
            message="Product saved successfully",
            data={
                "is_saved": True,
                "product_id": product.id,
                "saved_product_id": saved_product.id
            },
            status_code=201
        )
        
        
        
#save product list view
class SavedProductListView(APIView):
    permission_classes = [IsAuthenticated]
    paginator_class=CustomPagination
    def get(self, request):
        saved_products = SaveProduct.objects.filter(
            user=request.user
        ).select_related("product")

        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(saved_products, request)

        serializer = SaveProductSerializer(
            paginated_queryset,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response({
            "success": True,
            "status": 200,
            "message": "Saved products retrieved successfully",
            "products": serializer.data
        })