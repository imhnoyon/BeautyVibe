import datetime

from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from utils.api_response import APIResponse
from django.shortcuts import get_object_or_404
from .emails import *
from .serializers import *
from .utlis import *
from .models import *
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.utils import timezone
from Products.models import Order, Product, ProductCategory
from Products.ai_helper_function import build_ai_payload, send_to_ai_recommendation
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from UserAuthentication.models import User
from Products.models import Order
from UserProfile.models import Video, VideoView,Commission
from django.db.models import Count, Sum, F, DecimalField, ExpressionWrapper,Value,Q, ExpressionWrapper
from datetime import datetime
from Products.pagination import CustomPagination
from.serializers import UserListSerializer
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce   


# signup view for create a user .
class SignupView(CreateAPIView):
    permission_classes=[AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        # serializer.is_valid(raise_exception=True)
        user = serializer.save()
        code = generate_otp()
        VerificationCode.objects.create(
            user=user,
            code=code,
            expires_at=otp_expiry(),
            purpose="verify"
        )
        if user.email:
            send_verification_email(user.email, code)
        return APIResponse.success(
            message="User registered successfully!Send to code by email",
            data={
                "user_id": str(user.id),
            },
            status_code=status.HTTP_201_CREATED
        )

        
        
# -------Email Verification views ------------ #
class VerifyEmailView(APIView):
    def post(self, request):
        user = get_object_or_404(User, id=request.data.get("user_id"))
        Code = request.data.get("code")
        record = VerificationCode.objects.filter(user=user, code=Code, purpose="verify", expires_at__gte=timezone.now()).first()
        if not record:
            return APIResponse.error(message="Invalid code", status_code=status.HTTP_400_BAD_REQUEST)
        user.is_verified = True
        user.save()
        record.delete()
        tokens = generate_tokens(user)
        return APIResponse.success(
            message="Email Verification Successfully!",
            data={
                **tokens,
                "user_id": str(user.id),
            },
            status_code=status.HTTP_200_OK
        )
        
        
#-----signin view for all user role -------
class SignInView(APIView):
    def post(self, request):
        password = request.data.get("password")
        user = User.objects.filter(
            email=request.data.get("email")).first()
        if not user or not user.check_password(password):
            return APIResponse.error(message="Invalid credentials", status_code=status.HTTP_400_BAD_REQUEST)

        tokens = generate_tokens(user)

        return APIResponse.success(
            message="Login successful",
            data={
                **tokens,
                # "access_token": tokens.get("access"),
                # "refresh_token": tokens.get("refresh"),
                "user_id": str(user.id),
               
            }
        )
        
#--------Resend OTP for email verification and password reset ---------#
class ResendVerificationCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return APIResponse.error(message="Email is required", status_code=400)
        user = get_object_or_404(User, email=email)
        code = generate_otp()
        expires = otp_expiry()
        VerificationCode.objects.filter(user=user, purpose="verify").delete()
        VerificationCode.objects.create(
            user=user, 
            code=code, 
            expires_at=expires, 
            purpose="verify"
        )
        if user.email:
            send_verification_email(user.email, code)  
        return APIResponse.success(
            message="Resend code sent successfully. Please check your email!",
            data={
                "email": user.email,
                "expires_at": int(expires.timestamp() * 1000)
            }
        )
        
        
        
#-------Forgot pasword and reset password views ---------#
class ForgotPasswordView(APIView):
    def post(self, request):
        user = User.objects.filter(
            email=request.data.get("email")
        ).first()

        if not user:
            return APIResponse.error(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
        code = generate_otp()
        expires = otp_expiry()
        VerificationCode.objects.create( user=user, code=code, expires_at=expires, purpose="reset")
        if user.email:
            send_reset_password_email(user.email,code)   
        return APIResponse.success(
            message="Resset password code sent successfully.please check your email!",
            data={
                "user_id": str(user.id),
                "expires_at": int(expires.timestamp() * 1000)
            }
        )
        
        
        

# ------This view Verifies the resset code and returns a Secret key which is used to reset the pasword-----# 
class VerifyResetCodeView(APIView):
    def post(self, request):
        user = get_object_or_404(User, id=request.data.get("user_id"))
        record = VerificationCode.objects.filter(
            user=user,
            code=request.data.get("code"),
            purpose="reset",
            expires_at__gte=timezone.now()
        ).first()
        if not record:
            return APIResponse.error(message="Invalid code", status_code=status.HTTP_400_BAD_REQUEST)
        secret_key = str(uuid.uuid4())
        record.code = secret_key
        record.save()
        return APIResponse.success(
            message="Code verified successfully",
            data={"secret_key": secret_key,"user_id":user.id}
        )
    
    

# -----Reset password view --------#
class ResetPasswordView(APIView):
    def post(self, request):
        user = get_object_or_404(User, id=request.data.get("user_id"))
        # New password fields from the request
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        # Check if passwords match
        if new_password != confirm_password:
            return APIResponse.error(message="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST)

        record = VerificationCode.objects.filter(
            user=user,
            code=request.data.get("secret_key"),
            purpose="reset"
        ).first()
        if not record:
            return APIResponse.error(message="Invalid request", status_code=status.HTTP_400_BAD_REQUEST)
        # Update and save
        user.set_password(new_password)
        user.save()
        record.delete()
        return APIResponse.success(message="Password Reset Successful!", status_code=status.HTTP_200_OK)



#---------Custom token refresh view to refresh access token using refresh token----------#
class CustomTokenRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return APIResponse.error(message="Refresh token required", status_code=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            new_access = str(token.access_token)
            return APIResponse.success(
                message="Token refreshed successfully",
                data={"access_token": new_access}
            )
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        
        
        
        
#--------Google signin view --------#
class GoogleSignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleSignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['id_token']

        try:
            # Verify the token with Google
            # We use setting.GOOGLE_CLIENT_ID which should be defined in settings.py
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            # ID token is valid. Get user's Google info.
            # Reference: https://developers.google.com/identity/sign-in/web/backend-auth
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return APIResponse.error(message="Invalid issuer", status_code=status.HTTP_400_BAD_REQUEST)

            email = idinfo['email']
            google_id = idinfo['sub']
            full_name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')

            user, created = User.objects.get_or_create(email=email)

            if created:
                user.full_name = full_name
                user.google_id = google_id
                user.google_image_url = picture
                user.is_verified = True
                user.save()
            else:
                # If user exists but google_id is not set, set it
                if not user.google_id:
                    user.google_id = google_id
                    user.is_verified = True
                    user.save()

            tokens = generate_tokens(user)
            return APIResponse.success(
                message="Google Login successful",
                data={
                    **tokens,
                    "user_id": str(user.id),
                }
            )

        except ValueError:
            return APIResponse.error(message="Invalid token", status_code=status.HTTP_400_BAD_REQUEST)

    
    
#--------Get profile image view ---------#
from Products.ai_helper_function import send_to_ai_api, send_to_ai_recommendation
class GetProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        serializer = ProfileImageSerializer(request.user, context={'request': request})
        return APIResponse.success(
        message="Profile image retrieved successfully",
        data=serializer.data  
    )

    def post(self, request, *args, **kwargs):
        ai_api_key = request.headers.get("X-API-KEY")
        if not ai_api_key:
            return APIResponse.error(
                message="Missing AI API key in headers",
                status_code=400
            )
        user = request.user
        serializer = ProfileImageSerializer(
            instance=user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            image = user.profile_picture  
            
            # call ai helper function
            try:
                ai_response = send_to_ai_api(
                    user_id=user.id,
                    image=image,
                    api_key=ai_api_key
                )
                
                # Check if AI service returned an error dict instead of analysis
                if ai_response and "error" not in ai_response:
                    # Map AI response to user fields ONLY if no error
                    user.skin_tone = ai_response.get("skin_tone", user.skin_tone)
                    user.undertone = ai_response.get("undertone", user.undertone)
                    user.face_shape = ai_response.get("face_shape", user.face_shape)
                    user.eye_color = ai_response.get("eye_color", user.eye_color)
                    user.confidence_score = ai_response.get("confidence_score", user.confidence_score)
                    user.summary = ai_response.get("summary", user.summary)
                    user.save()
                    
                    message = "Profile image updated & analyzed successfully"
                else:
                    message = "Profile updated, but AI analysis failed"
                    
            except Exception as e:
                # Don't return error 500, just return success with a partial message
                ai_response = {"error": f"AI service failed: {str(e)}"}
                message = "Profile updated, but AI service was unreachable"

            # Return updated user data (including what we just saved)
            # Use original serializer to include full profile info
            final_serializer = ProfileImageSerializer(user, context={'request': request})
            return APIResponse.success(
                message=message,
                data={
    
                    "ai_raw_response": ai_response
                }
            )
          
        return APIResponse.error(
            message="Failed to update profile image",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        
#product Recommendation view based on user profile analysis and preferences
from Products.models import Product, ProductCategory
from Products.serializers import  RecommendationResponseSerializer


class ProductRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        products = Product.objects.select_related("category").all()
        categories = ProductCategory.objects.all()

        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return APIResponse.error(
                message="Missing AI API key in headers (X-API-KEY)",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        payload = build_ai_payload(
            user_profile=user,
            products=products,
            categories=categories,
            request=request
        )

        ai_result = send_to_ai_recommendation(
            payload=payload,
            api_key=api_key
        )

        if "error" in ai_result:
            return APIResponse.error(
                message=ai_result["error"],
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return APIResponse.success(
            message="Recommendations fetched successfully",
            data={
                # "sent_payload": payload,
                "ai_recommendations": ai_result
            },
            status_code=status.HTTP_200_OK
        )






#admin dashboard view for superuser to get insights about the platform like total users, total revenue, total videos, total views and top creators etc
class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get(self, request):
        # Top cards
        total_revenue = Order.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # total_users = User.objects.count()
        total_users = User.objects.filter(is_superuser=False).count()

        total_views = VideoView.objects.count()

        videos_posted = Video.objects.count()

        # Revenue trend by month
        revenue_trend = (
            Order.objects.filter(status='paid')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )

        revenue_dict = {
            item["month"].month: float(item["total"] or 0)
            for item in revenue_trend
        }
        revenue_chart = []
        for month in range(1, 13):
            revenue_chart.append({
                "month": datetime(2026, month, 1).strftime("%b"),
                "total": revenue_dict.get(month, 0)
            })

        user_growth = (
        User.objects.filter(is_superuser=False)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

        # Query result dictionary
        user_dict = {
            item["month"].month: item["total"]
            for item in user_growth
        }

        user_chart = []

        # Generate all 12 months
        for month in range(1, 13):
            user_chart.append({
                "month": datetime(2026, month, 1).strftime("%b"),
                "total": user_dict.get(month, 0)
            })

        # Top creators table
        top_creators = (
            User.objects.filter(creator=True)
            .annotate(
                total_videos=Count('product_videos_user', distinct=True),
                total_sales=Sum(
                ExpressionWrapper(
                    F('product_videos_user__product__orderitem__price') *
                    F('product_videos_user__product__orderitem__quantity'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            ),
                total_commission=Sum('commissions__commission_amount')
            )
            .order_by('-total_commission')[:5]
        )

        creators_data = []
        for creator in top_creators:
            creators_data.append({
                "id": str(creator.id),
                "name": creator.full_name,
                "email": creator.email,
                "videos": creator.total_videos or 0,
                "sales": float(creator.total_sales or 0),
                "commission": float(creator.total_commission or 0),
            })

        return Response({
            "cards": {
                "monthly_revenue": float(total_revenue),
                "total_users": total_users,
                "total_views": total_views,
                "videos_posted": videos_posted,
            },
            "revenue_trend": revenue_chart,
            "user_growth": user_chart,
            "top_creators": creators_data
        })
        
        
        



class UserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request, user_id=None):

        # USER DETAILS
        if user_id:
            user = get_object_or_404(
                User.objects.filter(is_superuser=False).prefetch_related(
                    "orders__items__product"
                ),
                id=user_id
            )

            serializer = UserDetailSerializer(
                user,
                context={"request": request}
            )

            return APIResponse.success(
                message="User details retrieved successfully",
                data=serializer.data
            )

        # USER LIST
        search = request.query_params.get("search")

        users = User.objects.filter(is_superuser=False,creator=False)

        if search:
            users = users.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)

        serializer = UserListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)
    
    
    
    
# user creator details view   
class UsercreatorAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request, user_id=None):

        # USER DETAILS
        if user_id:
            user = get_object_or_404(
                User.objects.filter(is_superuser=False).prefetch_related(
                    "orders__items__product"
                ),
                id=user_id
            )

            serializer = UserDetailSerializer(
                user,
                context={"request": request}
            )

            return APIResponse.success(
                message="User details retrieved successfully",
                data=serializer.data
            )

        # USER LIST
        search = request.query_params.get("search")

        users = User.objects.filter(is_superuser=False,creator=True)

        if search:
            users = users.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)

        serializer = UserListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)
    
    
    


class CreatorDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        
        creator = get_object_or_404(
            User.objects.filter(is_superuser=False, creator=True)
            .annotate(
                total_videos=Count("product_videos_user", distinct=True),
                total_views=Count("product_videos_user__views", distinct=True),
                total_earning=Coalesce(Sum("commissions__commission_amount"), Value(0, output_field=DecimalField())),
                total_orders=Count("commissions", distinct=True),
            ),
            id=user_id
        )

        serializer = CreatorDetailSerializer(
            creator,
            context={"request": request}
        )

        return APIResponse.success(
            message="Creator details retrieved successfully",
            data=serializer.data,
            status_code=200
        )
        
        
        
#admin profile can see and update his profile
class AdminProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        serializer = AdminUpdateprodileSerializer(
            request.user,
            context={"request": request}
        )
        return APIResponse.success(
            message="Profile retrieved successfully",
            data=serializer.data
        )

    def put(self, request):
        serializer = AdminUpdateprodileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                message="Profile updated successfully",
                data=serializer.data
            )

        return APIResponse.error(
            message="Failed to update profile",
            errors=serializer.errors,
            status_code=400
        )
        
        
        
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(old_password):
                return APIResponse.error(
                    message="Old password is incorrect",
                    status_code=400
                )

            user.set_password(new_password)
            user.save()

            return APIResponse.success(
                message="Password changed successfully"
            )

        return APIResponse.error(
            message="Failed to change password",
            errors=serializer.errors
        )