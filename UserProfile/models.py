from django.db import models
from UserAuthentication.models import User
from Products.models import Product


#--------this is video model--------
class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_videos_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_videos_product')
    caption = models.CharField(max_length=200)
    product_type = models.CharField(max_length=100)
    shade = models.CharField(max_length=200)
    video_url = models.FileField(upload_to='videos/',null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    saved_video = models.PositiveIntegerField(default=0)

    upload_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Video {self.id} by {self.user.full_name} for {self.product.name}"
        
        
        
#The model for video view count and user who view the video
class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # optional for anonymous
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    
    
    
class Commission(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commissions")
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name="commissions")

    order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def creator_name(self):
        if self.creator:
            return self.creator.full_name
        return None
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["creator"]),
        ]
        
    def __str__(self):
        return f"Commission for {self.creator.full_name} - Order: {self.order_amount}, Commission: {self.commission_amount}"
        
        
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")

    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "product")  

    def __str__(self):
        return f"{self.product.name} - {self.user.full_name} ({self.rating})"
    
    
    
    
    
class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    
    
class SavedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_videos")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="saved_by_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "video")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} saved Video {self.video.id}"
    
    
    
    
class LikedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_videos")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="liked_by_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "video")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} liked Video {self.video.id}"
    
    
    
    
class SharedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_videos")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="shared_by_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} shared Video {self.video.id}"