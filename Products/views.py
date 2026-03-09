from itertools import product

from django.shortcuts import render
from UserProfile.models import Commission, Video
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status
from .serializers import *
from .models import *
from utils.api_response import APIResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .pagination import CustomPagination
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Set stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# create product and list all products or retrieve single product also delete product
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    paginator_class =CustomPagination
    
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            product = serializer.save()
            return APIResponse.success(
                message="Product created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Failed to create product",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        
    # 🔹 LIST ALL PRODUCTS OR RETRIEVE SINGLE PRODUCT
    # def get(self, request, pk=None, *args, **kwargs):
    #     if pk:
    #         product = get_object_or_404(Product, pk=pk)
    #         serializer = ProductSerializer(product, context={'request': request})
    #         return APIResponse.success(
    #             message="Product retrieved successfully",
    #             data=serializer.data
    #         )
        
    #     products = Product.objects.all()
        
    #     # ✅ Apply Pagination
    #     paginator = self.paginator_class()
    #     paginated_products = paginator.paginate_queryset(products, request)
    #     serializer = ProductSerializer(paginated_products, many=True, context={'request': request})
        
    #     return APIResponse.success(
    #         message="Product list retrieved successfully",
    #         data={
    #             "total": products.count(),
    #             "page": paginator.page.number,
    #             "total_pages": paginator.page.paginator.num_pages,
    #             "next": paginator.get_next_link(),
    #             "previous": paginator.get_previous_link(),
    #             "products": serializer.data
    #         }
    #     )
    
    
    def get(self, request, pk=None, *args, **kwargs):
        status = request.query_params.get("status")
        search = request.query_params.get("search")
        category = request.query_params.get("category")

        if pk:
            product = get_object_or_404(Product, pk=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return APIResponse.success(
                message="Product retrieved successfully",
                data=serializer.data
            )

        products = Product.objects.all()

        # search filter
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(shade__icontains=search) |
                Q(category__name__icontains=search)
            )

        # category filter
        if category:
             products = products.filter(category__name__icontains=category)

        # যদি status field থাকে তাহলে এটা রাখো, না থাকলে remove করো
        if status:
            products = products.filter(status=status)

        paginator = self.paginator_class()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(
            paginated_products,
            many=True,
            context={'request': request}
        )

        return APIResponse.success(
            message="Product list retrieved successfully",
            data={
                "total": products.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "products": serializer.data
            }
        )
        
    
    def put(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,  
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                message="Product updated successfully",
                data=serializer.data
            )

        return APIResponse.error(
            message="Failed to update product",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
    # 🔹 DELETE PRODUCT
    def delete(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return APIResponse.success(
            message="Product deleted successfully",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT
        )




# Explore view with category filter and search Functionality
class ExploreView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    def get(self, request):
        category_slug = request.query_params.get('category')
        search_query = request.query_params.get('search')
        categories = ProductCategory.objects.all()
        category_serializer = ProductCategorySerializer(categories, many=True)
        products = Product.objects.all()
        if category_slug:
            products = products.filter(category__slug=category_slug)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
            
        total_products = products.count()
        # ✅ Apply Pagination ONLY to products
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)

        product_serializer = ProductListSerializer(
            paginated_products,
            many=True,
            context={'request': request}
        )
        # product_serializer = ProductListSerializer(products, many=True, context={'request': request})

        return APIResponse.success(
            message="Explore data retrieved successfully",
            data={
                "categories": category_serializer.data,
                "total_products": total_products,
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "products": product_serializer.data
            },
            status_code=status.HTTP_200_OK
        )

# Product details view with 
class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        video_id = request.query_params.get("video_id")
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, context={'request': request})
        
        return APIResponse.success(
            message="Product details retrieved successfully",
            data={
                "video_id": video_id,
                "product": serializer.data,
            }
        )

#save product view for user to save products to their profile
class SaveProductsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    # GET → List all saved products of user
    def get(self, request):
        saved_products = SaveProducts.objects.filter(
            user=request.user
        ).select_related('product')
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(saved_products, request)
        serializer = SavedProductSerializer(page, many=True, context={'request':request})

        return APIResponse.success(
            message="Saved products fetched successfully",
            data={
                "total": saved_products.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "products": serializer.data
            },
            status_code=status.HTTP_200_OK
        )
    def post(self, request):
        serializer = SavedProductSerializer(data=request.data,context={'request':request})

        if serializer.is_valid():
            product = serializer.validated_data['product']
            shade = serializer.validated_data.get('shade')
            colour_hex = serializer.validated_data.get('colour_hex')

            saved_product, created = SaveProducts.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={
                    'shade': shade,
                    'colour_hex': colour_hex
                }
            )

            if created:
                message = "Product Saved Successfully"
                status_code = status.HTTP_201_CREATED
            else:
                message = "Product Already Saved"
                status_code = status.HTTP_200_OK

            return APIResponse.success(
                message=message,
                data=SavedProductSerializer(saved_product).data,
                status_code=status_code
            )

        return APIResponse.error(
            message="Invalid data",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        
        

# save product delete view for user to delete saved products from their profile
class DeleteSaveProductsView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        try:
            delete_product = SaveProducts.objects.get(
                id=pk,
                user=request.user
            )
        except SaveProducts.DoesNotExist:
            return APIResponse.error(
                message='Save product not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

        delete_product.delete()

        return APIResponse.success(
            message= 'Save product deleted successfully',
            status_code=status.HTTP_200_OK
        )


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return APIResponse.success(
            message="Cart retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # If frontend sends video_id instead of video, DRF might ignore it. Let's inject it to be safe.
        data = request.data.copy()
        if "video_id" in data and "video" not in data:
            data["video"] = data["video_id"]
            
        serializer = CartItemSerializer(data=data)
        
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data.get('quantity', 1)
            shade = serializer.validated_data.get('shade')
            colour_hex = serializer.validated_data.get('colour_hex')
            video = serializer.validated_data.get('video')
            
            # Check if item already in cart
            cart_item = CartItems.objects.filter(
                cart=cart, 
                product=product,
                shade=shade
            ).first()
            
            if cart_item:
                cart_item.quantity += quantity
                cart_item.product_amount = cart_item.quantity * product.price
                if video: # Always attribution to latest video if they added more from it
                    cart_item.video = video
                cart_item.save()
            else:
                cart_item = CartItems.objects.create(
                    cart=cart,
                    product=product,
                    video=video,
                    shade=shade,
                    colour_hex=colour_hex,
                    quantity=quantity,
                    product_amount=quantity * product.price

                )
            
            return APIResponse.success(
                message="Item added to cart",
                data=CartItemSerializer(cart_item, context={'request': request}).data,
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Failed to add item to cart",
            errors=serializer.errors
        )


class CartItemUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        cart_item = get_object_or_404(CartItems, pk=pk, cart__user=request.user)
        serializer = CartItemSerializer(cart_item, context={'request': request})
        return APIResponse.success(
            message="Item retrieved successfully",
            data=serializer.data
        )

    def patch(self, request, pk):
        cart_item = get_object_or_404(CartItems, pk=pk, cart__user=request.user)
        quantity = request.data.get('quantity')
        
        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    cart_item.delete()
                    return APIResponse.success(message="Item removed from cart")
                
                cart_item.quantity = quantity
                # Ensure we have a product to calculate amount
                if cart_item.product:
                    cart_item.product_amount = cart_item.quantity * cart_item.product.price
                cart_item.save()
                
                return APIResponse.success(
                    message="Cart updated successfully",
                    data=CartItemSerializer(cart_item, context={'request': request}).data
                )
            except ValueError:
                return APIResponse.error(message="Invalid quantity value")
        
        return APIResponse.error(message="Quantity is required for update")

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItems, pk=pk, cart__user=request.user)
        cart_item.delete()
        return APIResponse.success(message="Item removed from cart")


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Pre-fill user data
        user = request.user
        data = {
            "full_name": user.full_name or "",
            "mobile_number": "", 
            "emirate": "",
            "area": "",
            "building_name": "",
            "apartment_no": "",
            "landmark": "",
            "delivery_methods": [
                {"id": "standard", "name": "Standard Delivery", "charge": 0, "note": "Within 2-3 days"},
                {"id": "next_day", "name": "Next-Day Delivery", "charge": 20, "note": "Today: 3-6 PM"},
                {"id": "same_day", "name": "Same-Day Delivery", "charge": 30, "note": "Today: 3-6 PM"}
            ]
        }
        return APIResponse.success(message="User info for checkout", data=data)

    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.cart_items.all()
        video_id = request.data.get("video_id")
        if not cart_items.exists():
            return APIResponse.error(message="Your cart is empty")

        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Calculate total and delivery charge
            delivery_method = serializer.validated_data.get('delivery_method', 'standard')
            delivery_charges = {
                'standard': 0,
                'next_day': 20,
                'same_day': 30
            }
            delivery_charge = delivery_charges.get(delivery_method, 0)
            
            cart_total = sum(item.product_amount for item in cart_items)
            total_amount = cart_total + delivery_charge
            
            # Create the Order
            order = serializer.save(
                user=user, 
                total_amount=total_amount,
                delivery_charge=delivery_charge
            )
            
            # Create OrderItems (Snapshots)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    video=item.video,
                    shade=item.shade,
                    colour_hex=item.colour_hex,
                    quantity=item.quantity,
                    price=item.product.price
                )
                
            cart_items.delete()
            
            return APIResponse.success(
                message="Order created successfully",
                data=OrderSerializer(order, context={'request': request}).data,
                status_code=status.HTTP_201_CREATED
            )
        
        return APIResponse.error(
            message="Invalid checkout data",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return APIResponse.error(message="Order ID is required")
            
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = order.items.all()

        if not order_items.exists():
            return APIResponse.error(message="Order has no items")

        line_items = []

        # Add products to line items
        for item in order_items:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{item.product.name} ({item.shade})" if item.shade else item.product.name,
                    },
                    "unit_amount": int(item.price * 100),
                },
                "quantity": item.quantity,
            })
            
        # Add delivery charge as a line item if > 0
        if order.delivery_charge > 0:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Delivery Charge ({order.get_delivery_method_display()})",
                    },
                    "unit_amount": int(order.delivery_charge * 100),
                },
                "quantity": 1,
            })

        try:
            from django.urls import reverse
            
            success_url = request.build_absolute_uri(reverse('payment-success')) + "?session_id={CHECKOUT_SESSION_ID}"
            cancel_url = request.build_absolute_uri(reverse('payment-cancel'))
            
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                customer_email=request.user.email,
                success_url=success_url,
                cancel_url=cancel_url,
                
                metadata={
                    "order_id": order.id
                }
            )

            # Link stripe session to order
            order.stripe_session_id = session.id
            order.status = 'pending'
            order.save()

            return APIResponse.success(
                message="Checkout session created",
                data={
                    "checkout_url": session.url,
                    "session_id": session.id
                },
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return APIResponse.error(message=f"Stripe error: {str(e)}")
            
from django.conf import settings     
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not sig_header:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        #detect payment method
        payment_intent_id = session.get("payment_intent")
        if not payment_intent_id:
            return HttpResponse(status=200)

        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        payment_method_id = payment_intent.get("payment_method")

        actual_payment_method = "unknown"

        if payment_method_id:
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)

            # Base type: card / link / paypal / etc.
            method_type = payment_method.type
            actual_payment_method = method_type

            # Wallet detect for Google Pay / Apple Pay
            if method_type == "card":
                card_data = getattr(payment_method, "card", None)

                # stripe-python objects usually support attribute access
                if card_data and getattr(card_data, "wallet", None):
                    wallet = card_data.wallet
                    wallet_type = getattr(wallet, "type", None)

                    if wallet_type == "google_pay":
                        actual_payment_method = "google_pay"
                    elif wallet_type == "apple_pay":
                        actual_payment_method = "apple_pay"
                    else:
                        actual_payment_method = "card"

        print("Detected Payment Method:", actual_payment_method)
        
        
        # We can use metadata to get order_id reliably
        order_id = session.get("metadata", {}).get("order_id")
        
        try:
            if order_id:
                order = Order.objects.get(id=order_id)
            else:
                # Fallback to session ID lookup
                order = Order.objects.get(stripe_session_id=session["id"])
                
            if not order.is_paid:
                order.is_paid = True
                order.status = 'paid' 
                order.save()
                
                
                COMMISSION_RATE = settings.COMMISSION_RATE
                for item in order.items.all():
                    if item.video and item.video.user:
                        # Calculate item total
                        item_total = item.price * item.quantity
                        commission_amount = float(item_total) * COMMISSION_RATE
                        # Create commission for the creator
                        Commission.objects.create(
                            creator=item.video.user,
                            video=item.video,
                            payment_method=actual_payment_method,
                            order_amount=item_total,
                            commission_amount=commission_amount
                        )

        except Order.DoesNotExist:
            print(f"Order not found for session {session['id']}")

    return HttpResponse(status=200)




# Category list and create category view for admin
class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    paginator_class = CustomPagination
    
    def get(self, request):
        categories = ProductCategory.objects.all().order_by("-id")

        paginator = self.paginator_class()
        paginated_queryset = paginator.paginate_queryset(categories, request)

        serializer = ProductCategorySerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Category list fetched successfully",
            "categories": serializer.data
        })


    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                message="Category created successfully",
                data=serializer.data,
                status_code=201
            )

        return APIResponse.error(
            message="Invalid data provided",
            errors=serializer.errors,
            status_code=400
        )
        
    def put(self, request, pk):
        category = get_object_or_404(ProductCategory, pk=pk)
        serializer = ProductCategorySerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                message="Category updated successfully",
                data=serializer.data
            )

        return APIResponse.error(
            message="Invalid data provided",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        category = get_object_or_404(ProductCategory, pk=pk)
        serializer = ProductCategorySerializer(
            category, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                message="Category partially updated successfully",
                data=serializer.data
            )

        return APIResponse.error(
            message="Invalid data provided",
            errors=serializer.errors
        )

    
    def delete(self, request, pk):
        category = get_object_or_404(ProductCategory, pk=pk)
        category.delete()

        return APIResponse.success(
            message="Category deleted successfully",
            status_code=204
        )
        
        

# # Products details view for explore from video 
# class ProductDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, product_id):
#         video_id = request.query_params.get("video_id")

#         product = get_object_or_404(Product, id=product_id)

#         serializer = ProductSerializer(product, context={"request": request})

#         return APIResponse.success(
#             message="Product details retrieved successfully",
#             data={
#                 "product": serializer.data,
#                 "video_id": video_id
#             }
#         )




class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        if pk:
            order = get_object_or_404(
                Order.objects.prefetch_related("items"),
                pk=pk
            )
            serializer = OrderListSerializer(order, context={"request": request})
            return APIResponse.success(
                message="Order retrieved successfully",
                data=serializer.data
            )

        search = request.query_params.get("search")
        status_filter = request.query_params.get("status")

        orders = Order.objects.prefetch_related("items").all().order_by("-created_at")

        if search:
            orders = orders.filter(
                Q(full_name__icontains=search) |
                Q(mobile_number__icontains=search) |
                Q(id__icontains=search)
            )

        if status_filter:
            orders = orders.filter(status=status_filter)

        paginator = self.pagination_class()
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderListSerializer(
            paginated_orders,
            many=True,
            context={"request": request}
        )

        return APIResponse.success(
            message="Order list retrieved successfully",
            data={
                "total": orders.count(),
                "page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "orders": serializer.data
            }
        )
        
    def delete(self, request, pk=None):
        if not pk:
            return APIResponse.error(
                message="Order id is required",
                status_code=400
            )

        order = get_object_or_404(Order, pk=pk)
        order.delete()

        return APIResponse.success(
            message="Order deleted successfully",
            data=None,
            status_code=200
        )