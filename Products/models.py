from django.db import models
from django.utils.text import slugify
from BeautyVibe import settings
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
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products', null=True)  
    colour_hex = models.CharField(max_length=7, null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    video_url =models.FileField(upload_to='product_videos/',null=True,blank=True)
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
    

#the model is add product in cart for buy---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
#the model for hold all product---
class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_products')
    video = models.ForeignKey('UserProfile.Video', on_delete=models.SET_NULL, null=True, blank=True, related_name='video_cart_items')
    # look = models.ForeignKey(LookProducts, on_delete=models.PROTECT, related_name='cart_looks')
    shade = models.CharField(max_length=200, null=True, blank=True)
    colour_hex = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    product_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.cart.user.email


# --- Order and Checkout Models ---
class Order(models.Model):
    DELIVERY_METHODS = (
        ('standard', 'Standard Delivery'),
        ('next_day', 'Next-Day Delivery'),
        ('same_day', 'Same-Day Delivery'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20)
    emirate = models.CharField(max_length=100)
    area = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255)
    apartment_no = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='standard')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_note = models.TextField(null=True, blank=True)
    
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def number_of_items(self):
        if hasattr(self, 'items'):
            return self.items.count()
    def __str__(self):
        return f"Order {self.id} by {self.full_name}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    video = models.ForeignKey('UserProfile.Video', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items_video')
    shade = models.CharField(max_length=200, null=True, blank=True)
    colour_hex = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown Product'}"
    
    
    
    
    
class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order.id} - {self.status}"