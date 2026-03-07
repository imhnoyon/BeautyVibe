from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', SignInView.as_view(), name='login'),
    path('resend-verification/', ResendVerificationCodeView.as_view(), name='resend-verification'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-reset-code/', VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('refresh-token/', CustomTokenRefreshView.as_view(), name='refresh-token'),
    path('google-login/', GoogleSignInView.as_view(), name='google-login'),
    
    
    # Product recommendation endpoint by AI
    path('set-image-image/', GetProfileImageView.as_view(), name='set-image'),
    # path('recommendations/', ProductRecommendationView.as_view(), name='product-recommendations'),
    path("recommendations/", ProductRecommendationView.as_view(), name="product-recommendations"),
    
    
    
    #admin dashboard
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    path("users/", UserAPIView.as_view()),
    path("users/<uuid:user_id>/", UserAPIView.as_view()),
    path("users-creators/", UsercreatorAPIView.as_view()),
    path("users-creators/<uuid:user_id>/", UsercreatorAPIView.as_view()),
    
    
    
    
]