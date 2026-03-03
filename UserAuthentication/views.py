from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from utils.api_response import APIResponse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .emails import *
from .serializers import *
from .utlis import *
from .models import *
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from rest_framework.response import Response
from django.utils import timezone

# signup view for create a user .
class SignupView(CreateAPIView):
    permission_classes=[AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
class GetProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        serializer = ProfileImageSerializer(request.user, context={'request': request})
        profile_picture = serializer.data.get('profile_picture')
        return APIResponse.success(
            message="Profile image retrieved successfully",
            data={'image': profile_picture, 'user_id': str(request.user.id)}
        )

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfileImageSerializer(instance=user, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                message="Profile image updated successfully",
                data={
                    "image": serializer.data,
                    "user_id": str(user.id),
                }
            )
           
        else:
            return APIResponse.error(
                message="Failed to update profile image",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )