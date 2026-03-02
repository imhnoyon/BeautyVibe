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
    
]