from django.urls import path
from .views import VideoUploadView

urlpatterns = [
    path('product-video-upload/', VideoUploadView.as_view(), name='product-video-upload'),
]