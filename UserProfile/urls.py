from django.urls import path
from .views import *

urlpatterns = [
    path("categories-list/", ProductCategoryListView.as_view()),
    path("categories/products/<int:category_id>/", ProductByCategoryView.as_view()),
    path("products/upload-video/<int:product_id>/",ProductVideoUploadView.as_view(), name="upload-product-video"),
    path("user-videos/", UserVideoListView.as_view(), name="user-videos"),
    path("videos/watch/<int:video_id>/", VideoWatchView.as_view(), name="video-watch"),
    
    # ✅ creator dashboard
    path("creator/dashboard/", CreatorDashboardView.as_view(), name="creator-dashboard"),
    
     # product reviews
    path("reviews/<int:product_id>/", ProductReviewView.as_view(), name="product-reviews"),
    
    path("orders/history/", OrderHistoryView.as_view(), name="order-history")
]