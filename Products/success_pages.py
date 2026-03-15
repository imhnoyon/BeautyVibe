import stripe
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Order, PaymentHistory
from UserProfile.models import Commission
from django.db import transaction
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get("session_id")

        if not session_id:
            return render(request, "Products/payment_success.html", {"order_id": "N/A", "amount": "0.00"})

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            order_id = session.metadata.get("order_id", "N/A")
            amount = session.amount_total / 100 if session.amount_total else 0
            
            # Fallback: Process order if webhook hasn't done it yet
            if order_id != "N/A":
                try:
                    with transaction.atomic():
                        order = Order.objects.select_for_update().filter(id=order_id).first()
                        if order and not order.is_paid:
                            order.is_paid = True
                            order.status = 'paid'
                            order.save()
                            
                            # Commission Logic (Duplicate check handled by is_paid)
                            COMMISSION_RATE = getattr(settings, 'COMMISSION_RATE', 0.10)
                            for item in order.items.all():
                                if item.video and item.video.user:
                                    item_total = item.price * item.quantity
                                    commission_amount = item_total * Decimal(str(COMMISSION_RATE))
                                    Commission.objects.get_or_create(
                                        creator=item.video.user,
                                        video=item.video,
                                        order_amount=item_total,
                                        defaults={'commission_amount': commission_amount, 'payment_method': 'card'}
                                    )
                            
                            # Payment History
                            PaymentHistory.objects.get_or_create(
                                stripe_session_id=session.id,
                                defaults={
                                    'user': order.user,
                                    'order': order,
                                    'transaction_method': 'card',
                                    'amount': order.total_amount
                                }
                            )
                except Exception as e:
                    print(f"Fallback processing error: {str(e)}")

            return render(request, "Products/payment_success.html", {
                "order_id": order_id,
                "amount": f"{amount:.2f}",
                "session_id": session.id
            })

        except Exception as e:
            return render(request, "Products/payment_success.html", {"order_id": "Error", "amount": "0.00"})
            
            
class StripePaymentCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, "Products/payment_cancel.html")
    
    
class stripe_reauth_page(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return render(request, "Products/reauth.html")

class stripe_return_page(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return render(request, "Products/return.html")