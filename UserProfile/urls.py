from django.urls import path
from .views import *
from Products.views import SaveProductsView
urlpatterns = [
    path("categories-list/", ProductCategoryListView.as_view()),
    path("categories/products/<int:category_id>/", ProductByCategoryView.as_view()),
    path("products/upload-video/<int:product_id>/",ProductVideoUploadView.as_view(), name="upload-product-video"),
    path("user-videos/", UserVideoListView.as_view(), name="user-videos"),
    path("creator-videos/", UserOwnVideoListView.as_view(), name="creator-videos"),
    path("videos/watch/<int:video_id>/", VideoWatchView.as_view(), name="video-watch"),
    
    # ✅ creator dashboard
    path("creator/dashboard/", CreatorDashboardView.as_view(), name="creator-dashboard"),
    
     # product reviews
    path("reviews/<int:product_id>/", ProductReviewView.as_view(), name="product-reviews"),
    
    path("orders/history/", OrderHistoryView.as_view(), name="order-history"),
    
    
    
    #commission tracking for creator
    path("commissions/", CommissionTrackingAPIView.as_view(), name="commission-list"),
    path("commissions/<int:pk>/", CommissionTrackingAPIView.as_view(), name="commission-detail"),
    
    
    # added privacy policy view for user to see the privacy policy of the app
    path("policies/", PrivacyPolicyAPIView.as_view()),
    path("policies/<int:pk>/", PrivacyPolicyAPIView.as_view()),
    
    
    #saved video view for user to see the saved video and also remove the saved video from the list
    path("videos/save/<int:video_id>/", SaveUnsaveVideoAPIView.as_view(), name="save-unsave-video"),
    path("videos/saved/", SavedVideoListAPIView.as_view(), name="saved-video-list"),
    
    
    # liked video view for user to see the liked video and also remove the liked video from the list
    path("videos/like/<int:video_id>/", LikeUnlikeVideoAPIView.as_view(), name="like-unlike-video"),
    path("videos/liked/", LikedVideoListAPIView.as_view(), name="liked-video-list"),
    
    
    # shared video view for user to see the shared video and also remove the shared video from the list
    path("videos/share/<int:video_id>/", ShareVideoAPIView.as_view(), name="share-video"),
    path("videos/shared/", SharedVideoListAPIView.as_view(), name="shared-video-list"),
    
    #product save unsave
    path("products/save-unsave/<int:product_id>/", SaveUnsaveProductView.as_view(), name="save-unsave-product"),
    path("saved-products/", SavedProductListView.as_view(), name="saved-product-list"),
]