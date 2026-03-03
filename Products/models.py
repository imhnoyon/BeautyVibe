from django.db import models
from django.utils.text import slugify
from UserAuthentication.models import User


# product Category create for product
def generate_unique_slug(model, value):
    slug = slugify(value)
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{slugify(value)}-{counter}"
        counter += 1
    return slug

class ProductCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    # descriptions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ProductCategory, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True)  # increase to 200
    brand = models.CharField(max_length=200)
    shade = models.CharField(max_length=200)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')  # plural
    colour_hex = models.CharField(max_length=7, null=True, blank=True)  # optional: store hex code properly (#RRGGBB)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
    
#this model for look save that same user can use again the look--
class SavedLook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='looks_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='look_product', null=True)
    colour_hex = models.CharField(max_length=9)
    shade = models.CharField(max_length=100)
    user_image = models.URLField(null=True)
    name = models.CharField(max_length=200, null=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','product','shade')

def __str__(self):
        return f"{self.user}'s saved {self.product} - {self.shade}"
    
    
    
    
#the model for saved product-------------
class SaveProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_entries')
    shade = models.CharField(max_length=200)
    colour_hex = models.CharField(max_length=200, null=True, blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return self.product.name
    


#-this is video model--
class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_videos')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_videos')
    # look = models.ForeignKey(LookProducts, on_delete=models.PROTECT, related_name='look_videos')
    caption = models.CharField(max_length=200)
    product_type = models.CharField(max_length=100)
    product_tag = models.CharField(max_length=200, null=True, blank=True)
    shade = models.CharField(max_length=200)
    video_url = models.URLField(null=True, blank=True)
    # thumbnail = models.URLField(null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    saved_video = models.PositiveIntegerField(default=0)

    upload_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']


#the model is add product in cart for buy---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    
#the model for hold all product---
class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_products')
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name='video_cart_items')
    # look = models.ForeignKey(LookProducts, on_delete=models.PROTECT, related_name='cart_looks')
    shade = models.CharField(max_length=200, null=True, blank=True)
    colour_hex = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    product_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.cart.user.username