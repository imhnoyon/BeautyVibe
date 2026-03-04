from django.db import models
from UserAuthentication.models import User
from Products.models import Product


#--------this is video model--------
class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_videos_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_videos_product')
    # look = models.ForeignKey(LookProducts, on_delete=models.PROTECT, related_name='look_videos')
    caption = models.CharField(max_length=200)
    product_type = models.CharField(max_length=100)
    product_tag = models.CharField(max_length=200, null=True, blank=True)
    shade = models.CharField(max_length=200)
    video_url = models.FileField(upload_to='videos/',null=True, blank=True)
    # thumbnail = models.URLField(null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    saved_video = models.PositiveIntegerField(default=0)

    upload_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']