# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from Products.models import Product, Video
from .serializers import *
from utils.api_response import APIResponse  

class VideoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VideoUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        video = serializer.save()  

        return APIResponse.success(
            message="Video uploaded successfully",
            data=VideoUploadSerializer(video).data
        )
        
        
