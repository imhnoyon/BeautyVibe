from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import Video
from .serializers import VideoUploadSerializer
from utils.api_response import APIResponse

class VideoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VideoUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            video = serializer.save()
            return APIResponse.success(
                message="Video uploaded successfully",
                data=VideoUploadSerializer(video, context={'request': request}).data,
                status_code=status.HTTP_201_CREATED
            )
        
        return APIResponse.error(
            message="Failed to upload video",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
