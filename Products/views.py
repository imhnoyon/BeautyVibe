from itertools import product

from django.shortcuts import render
from UserProfile.models import Commission, Video
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .serializers import *
from .models import *
from utils.api_response import APIResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q, Case, When, DecimalField, Value
from .pagination import CustomPagination
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.urls import reverse
from .utils import *
from django.db import transaction


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
            # Retrieve video object if video_id is passed at checkout as a fallback
            checkout_video = None
            if video_id:
                try:
                    checkout_video = Video.objects.filter(id=video_id).first()
                except Exception:
                    pass

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    video=item.video or checkout_video,
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
                    "order_id": str(order.id)
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
 
@csrf_exempt
def stripe_webhook(request):
    # Merge all webhook logic into one function (handles both checkout and payout)
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not sig_header:
        return HttpResponse("Missing signature", status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print(f"DEBUG Webhook Signature Error: {str(e)}")
        return HttpResponse(f"Invalid payload: {str(e)}", status=400)

    event_type = event["type"]
    session = event["data"]["object"]
    print(f"DEBUG: Webhook received for type {event_type} and session/obj {session.get('id')}")

    # --- 1. HANDLE CHECKOUT SESSION COMPLETED ---
    if event_type == "checkout.session.completed":
        # Detect payment method info safely
        actual_payment_method = "stripe"
        payment_intent_id = session.get("payment_intent")
        
        if payment_intent_id:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                payment_method_id = payment_intent.get("payment_method")

                if payment_method_id:
                    payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
                    actual_payment_method = getattr(payment_method, "type", "stripe")

                    # Wallet detect for Google Pay / Apple Pay
                    if actual_payment_method == "card":
                        card_data = getattr(payment_method, "card", None)
                        if card_data and getattr(card_data, "wallet", None):
                            wallet = card_data.wallet
                            wallet_type = getattr(wallet, "type", None)
                            if wallet_type in ["google_pay", "apple_pay"]:
                                actual_payment_method = wallet_type
            except Exception as e:
                print(f"DEBUG Error retrieving stripe payment details: {str(e)}")

        # Use metadata or session ID for lookup
        order_id = session.get("metadata", {}).get("order_id")
        session_id = session.get("id")
        print(f"DEBUG Checkout Payload: order_id={order_id}, session_id={session_id}")
        
        try:
            with transaction.atomic():
                order = None
                if order_id:
                    order = Order.objects.select_for_update().filter(id=order_id).first()
                if not order:
                    order = Order.objects.select_for_update().filter(stripe_session_id=session_id).first()
                
                if order:
                    print(f"DEBUG: Found Order {order.id}. is_paid={order.is_paid}")
                    if not order.is_paid:
                        order.is_paid = True
                        order.status = 'paid' 
                        order.save()
                        print(f"DEBUG: Order {order.id} marked as paid successfully.")
                        
                        # COMMISSION LOGIC: Re-verify items have video attached
                        COMMISSION_RATE = getattr(settings, 'COMMISSION_RATE', 0.10)
                        from decimal import Decimal
                        order_items = order.items.all()
                        print(f"DEBUG: Order {order.id} has {order_items.count()} items.")
                        
                        for item in order_items:
                            print(f"DEBUG: Processing item {item.id}, video={'linked' if item.video else 'null'}")
                            if item.video:
                                if item.video.user:
                                    item_total = item.price * item.quantity
                                    comm_amount = item_total * Decimal(str(COMMISSION_RATE))
                                    
                                    commission = Commission.objects.create(
                                        creator=item.video.user,
                                        video=item.video,
                                        payment_method=actual_payment_method,
                                        order_amount=item_total,
                                        commission_amount=comm_amount
                                    )
                                    # print(f"DEBUG: Commission {commission.id} created for Creator {item.video.user.id} from Video {item.video.id}")
                                else:
                                    return APIResponse.error(message=f"Item {item.id} has video with no user/creator", status_code=400)
                            else:
                                return APIResponse.error(message=f"Item {item.id} has no video linked", status_code=400)
                    
                    # Payment History
                    if not PaymentHistory.objects.filter(stripe_session_id=session_id).exists():
                        PaymentHistory.objects.create(
                            user=order.user,
                            order=order,
                            transaction_method=actual_payment_method,
                            amount=order.total_amount,
                            stripe_session_id=session_id
                        )
                       
                else:
                    return APIResponse.error(message="Order not found for this session", status_code=404)
        except Exception as e:
            return APIResponse.error(message="An error occurred while processing the webhook", status_code=500)

    # --- 2. HANDLE PAYOUT EVENTS (Withdrawal) ---
    elif event_type == "payout.paid":
        payout_id = session.get("id")
        withdrawal = CreatorWithdrawal.objects.filter(stripe_payout_id=payout_id).first()
        if withdrawal:
            withdrawal.status = "completed"
            withdrawal.save(update_fields=["status", "updated_at"])
            print(f"DEBUG: Withdrawal {withdrawal.withdraw_id} marked COMPLETED.")

    elif event_type == "payout.failed":
        payout_id = session.get("id")
        withdrawal = CreatorWithdrawal.objects.filter(stripe_payout_id=payout_id).first()
        if withdrawal:
            withdrawal.status = "failed"
            withdrawal.failure_reason = session.get("failure_message") or "Payout failed"
            withdrawal.save(update_fields=["status", "failure_reason", "updated_at"])
            print(f"DEBUG: Withdrawal {withdrawal.withdraw_id} marked FAILED.")

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
        
        


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        search = request.query_params.get("search")

        payments = PaymentHistory.objects.all().order_by("-created_at")

        # Search filter
        if search:
            payments = payments.filter(
                Q(payment_id__icontains=search) |
                Q(transaction_method__icontains=search)
            )

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(payments, request)

        serializer = PaymentHistorySerializer(paginated_queryset, many=True)

        return APIResponse.success(
            message="Payment history retrieved successfully",
            data={
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data
            }
        )
        
        
#For Withdrawn views

class CreateConnectAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.creator:
            return APIResponse.error(
                message="Only creators can connect Stripe account.",
                status_code=403
            )

        try:
            if not user.stripe_account_id:
                account = stripe.Account.create(
                    type="express",
                    country="US",  # need to set supported country for your business/user
                    email=user.email,
                    capabilities={
                        "transfers": {"requested": True},
                    },
                )
                user.stripe_account_id = account.id
                user.save(update_fields=["stripe_account_id"])
            else:
                account = stripe.Account.retrieve(user.stripe_account_id)

            refresh_url = request.build_absolute_uri(reverse('stripe-reauth'))
            return_url = request.build_absolute_uri(reverse('stripe-return'))

            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=refresh_url,
                return_url=return_url,
                type="account_onboarding",
            )

            return APIResponse.success(
                message="Stripe onboarding link generated successfully",
                data={
                    "stripe_account_id": account.id,
                    "onboarding_url": account_link.url,
                    "charges_enabled": account.get("charges_enabled", False),
                    "payouts_enabled": account.get("payouts_enabled", False),
                    "details_submitted": account.get("details_submitted", False),
                }
            )
        except stripe.error.StripeError as e:
            return APIResponse.error(
                message=f"Stripe error: {str(e)}",
                status_code=400
            )
            
            
#Creator login own deshboard
class StripeDashboardLoginLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.stripe_account_id:
            return APIResponse.error(
                message="Stripe account not connected.",
                status_code=400
            )

        try:
            login_link = stripe.Account.create_login_link(user.stripe_account_id)
            return APIResponse.success(
                message="Login link created successfully",
                data={"url": login_link.url}
            )
        except stripe.error.StripeError as e:
            return APIResponse.error(
                message=f"Stripe error: {str(e)}",
                status_code=400
            )
            
            
# Withdraw Request views
class CreatorWithdrawRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        if not user.creator:
            return APIResponse.error(
                message="Only creators can withdraw.",
                status_code=403
            )

        amount = request.data.get("amount")
        if not amount:
            return APIResponse.error(
                message="Amount is required.",
                status_code=400
            )

        try:
            amount = Decimal(str(amount))
        except Exception:
            return APIResponse.error(
                message="Invalid amount format.",
                status_code=400
            )

        if amount <= 0:
            return APIResponse.error(
                message="Amount must be greater than 0.",
                status_code=400
            )

        available_balance = get_creator_available_balance(user)

        if amount > available_balance:
            return APIResponse.error(
                message=f"Insufficient balance. Available balance is {available_balance}.",
                status_code=400
            )

        stripe_status = refresh_stripe_account_status(user)
        if not stripe_status:
            return APIResponse.error(
                message="No connected Stripe account found. Please connect Stripe first.",
                status_code=400
            )

        if not stripe_status["details_submitted"]:
            return APIResponse.error(
                message="Stripe onboarding is not completed.",
                status_code=400
            )

        if not stripe_status["payouts_enabled"]:
            return APIResponse.error(
                message="Stripe payouts are not enabled for this account.",
                status_code=400
            )

        withdrawal = CreatorWithdrawal.objects.create(
            creator=user,
            amount=amount,
            previous_balance=available_balance,
            current_balance=available_balance - amount,
            status="pending",
        )

        return APIResponse.success(
            message="Withdrawal request submitted successfully",
            data={
                "withdraw_id": withdrawal.withdraw_id,
                "amount": str(withdrawal.amount),
                "previous_balance": str(withdrawal.previous_balance),
                "current_balance": str(withdrawal.current_balance),
                "status": withdrawal.status,
            }
        )
        
        
#Admin pending withdrawn request list
from django.core.paginator import Paginator
class AdminWithdrawalListView(APIView):
    permission_classes = [IsAdminUser]
    # paginator_class=CustomPagination
    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        summary = CreatorWithdrawal.objects.aggregate(
            total_pending_amount=Sum(
                Case(
                    When(status="pending", then="amount"),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
            total_completed_amount=Sum(
                Case(
                    When(status="completed", then="amount"),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
        )

        stats = CreatorWithdrawal.objects.aggregate(
            total_withdrawals=Count("id"),
            total_completed=Count("id", filter=Q(status="completed")),
            total_rejected=Count("id", filter=Q(status="rejected")),
            total_pending=Count("id", filter=Q(status="pending")),
            total_processing=Count("id", filter=Q(status="processing")),
        )

        withdrawals = CreatorWithdrawal.objects.select_related("creator")\
            .filter(status="pending")\
            .order_by("-requested_at")

        paginator = Paginator(withdrawals, page_size)
        page_obj = paginator.get_page(page)

        pending_data = []
        for w in page_obj.object_list:
            pending_data.append({
                "id": w.id,
                "withdraw_id": w.withdraw_id,
                "creator_id": str(w.creator.id),
                "creator_name": w.creator.full_name,
                "creator_email": w.creator.email,
                "amount": float(w.amount),
                "previous_balance": float(w.previous_balance),
                "current_balance": float(w.current_balance),
                "status": w.status,
                "requested_at": w.requested_at,
            })

        return APIResponse.success(
            message="Withdrawal list fetched successfully",
            data={
                "summary": {
                    "total_pending_amount": float(summary["total_pending_amount"] or Decimal("0.00")),
                    "total_completed_amount": float(summary["total_completed_amount"] or Decimal("0.00")),
                    "total_withdrawals": stats["total_withdrawals"],
                    "total_completed": stats["total_completed"],
                    "total_rejected": stats["total_rejected"],
                    "total_pending": stats["total_pending"],
                    "total_processing": stats["total_processing"],
                },
                "pagination": {
                    "total_records": paginator.count,
                    "total_pages": paginator.num_pages,
                    "current_page": page_obj.number,
                    "page_size": page_size,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                },
                "pending_withdrawals": pending_data,
            }
        )
        
        
#Admin approve or reject withdraw request
class ApproveWithdrawalView(APIView):
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request):
        withdrawal_id = request.data.get("id")
        new_status = request.data.get("status")  # approved / rejected

        if not withdrawal_id:
            return APIResponse.error(
                message="Withdrawal ID is required.",
                status_code=400
            )

        if new_status not in ["approved", "rejected"]:
            return APIResponse.error(
                message="Status must be approved or rejected.",
                status_code=400
            )

        try:
            withdrawal = CreatorWithdrawal.objects.select_related("creator").get(
                id=withdrawal_id,
                status="pending"
            )
        except CreatorWithdrawal.DoesNotExist:
            return APIResponse.error(
                message="Invalid or already processed withdrawal.",
                status_code=404
            )

        # Reject
        if new_status == "rejected":
            withdrawal.status = "rejected"
            withdrawal.failure_reason = "Rejected by admin"
            withdrawal.save(update_fields=["status", "failure_reason", "updated_at"])

            return APIResponse.success(
                message="Withdrawal rejected successfully"
            )

        user = withdrawal.creator

        if not user.stripe_account_id:
            return APIResponse.error(
                message="Creator has no connected Stripe account.",
                status_code=400
            )

        stripe_status = refresh_stripe_account_status(user)
        if not stripe_status:
            return APIResponse.error(
                message="Unable to verify Stripe account.",
                status_code=400
            )

        if not stripe_status["details_submitted"]:
            return APIResponse.error(
                message="Creator has not completed Stripe onboarding.",
                status_code=400
            )

        if not stripe_status["payouts_enabled"]:
            return APIResponse.error(
                message="Payouts are disabled for this creator.",
                status_code=400
            )

        try:
            # Check platform balance
            balance = stripe.Balance.retrieve()
            available_usd = sum(
                b["amount"] for b in balance["available"]
                if b["currency"] == "usd"
            )

            amount_cents = int(withdrawal.amount * 100)

            if available_usd < amount_cents:
                return APIResponse.error(
                    message="Platform has insufficient Stripe balance.",
                    status_code=400
                )

            # 1) Transfer platform balance -> connected account
            transfer = stripe.Transfer.create(
                amount=amount_cents,
                currency="usd",
                destination=user.stripe_account_id,
                description=f"Creator withdrawal {withdrawal.withdraw_id}",
            )

            # 2) Optional manual payout connected account -> bank/debit card
            payout = stripe.Payout.create(
                amount=amount_cents,
                currency="usd",
                stripe_account=user.stripe_account_id,
            )
            
            payout_info = get_connected_account_payout_info(user.stripe_account_id)
            
            withdrawal.stripe_transfer_id = transfer.id
            withdrawal.stripe_payout_id = payout.id
            withdrawal.withdraw_method = payout_info["withdraw_method"]
            withdrawal.bank_name = payout_info["bank_name"]
            withdrawal.bank_last4 = payout_info["bank_last4"]

            withdrawal.status = "completed"
            withdrawal.save(update_fields=[
                "stripe_transfer_id",
                "stripe_payout_id",
                "status",
                "withdraw_method",
                "bank_name",
                "bank_last4",
                "updated_at",
            ])

            return APIResponse.success(
                message="Withdrawal approved and payout initiated successfully",
                data={
                    "transfer_id": transfer.id,
                    "payout_id": payout.id,
                    "status": withdrawal.status,
                }
            )

        except stripe.error.StripeError as e:
            withdrawal.status = "failed"
            withdrawal.failure_reason = str(e)
            withdrawal.save(update_fields=["status", "failure_reason", "updated_at"])

            return APIResponse.error(
                message=f"Stripe payout failed: {str(e)}",
                status_code=400
            )
            
            
#Withdraw list for Creator-user
class WithdrawHistoryListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        search = request.query_params.get("search")

        withdrawals = CreatorWithdrawal.objects.filter(
            creator=user
        ).order_by("-requested_at")

        if search:
            withdrawals = withdrawals.filter(
                Q(withdraw_id__icontains=search) |
                Q(status__icontains=search)
            )

        paginator = self.pagination_class()
        paginated_withdrawals = paginator.paginate_queryset(withdrawals, request)

        serializer = WithdrawHistorySerializer(
            paginated_withdrawals,
            many=True
        )

        return APIResponse.success(
            message="Withdraw history retrieved successfully",
            data={
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "withdrawals": serializer.data
            }
        )