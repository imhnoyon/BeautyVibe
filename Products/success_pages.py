import stripe
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Order

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
    
    
    
from django.shortcuts import render
class stripe_reauth_page(APIView):
    def get(request):
        return render(request, "Products/reauth.html")

class stripe_return_page(APIView):
    def get(request):
        return render(request, "Products/return.html")