from django.urls import path

from Products.success_pages import StripePaymentCancelView, StripePaymentSuccessView
from .views import *
from .success_pages import *
urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductCreateView.as_view(), name='product-detail'),
    path('categories/', ProductCategoryView.as_view(), name='category-list-create'),
    path("categories/<int:pk>/", ProductCategoryView.as_view(), name="category-detail"),
    path('explore/', ExploreView.as_view(), name='explore'),
    path('explore/<int:pk>/', ProductDetailView.as_view(), name='explore-detail'),
    path('save-product/', SaveProductsView.as_view(), name='save-product'),
    path('delete-save-product/<int:pk>/', DeleteSaveProductsView.as_view(), name='delete-save-product'),
    
    #orders urls
    path("orders/", OrderListAPIView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderListAPIView.as_view(), name="order-detail"),
    
    # Cart URLs
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/item/<int:pk>/', CartItemUpdateDeleteView.as_view(), name='cart-item-detail'),
    
    # Checkout URL
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    
    #payment history url for admin dashboard
    path("payment-history/", PaymentHistoryView.as_view(), name="payment-history"),
    
    #For withdraw
    path("creator/stripe/connect/", CreateConnectAccountView.as_view()),
    path("creator/stripe/dashboard-link/", StripeDashboardLoginLinkView.as_view()),
    path("creator/withdraw/request/", CreatorWithdrawRequestView.as_view()),
    path("admin/withdrawals/", AdminWithdrawalListView.as_view()),
    path("admin/withdrawals/action/", ApproveWithdrawalView.as_view()),
    path("stripe/webhook/", stripe_webhook),
    
    path("payment-success/", StripePaymentSuccessView.as_view(), name="payment-success"),
    path("payment-cancel/", StripePaymentCancelView.as_view(), name="payment-cancel"),
    
    path("stripe/reauth/", stripe_reauth_page.as_view(), name="stripe-reauth"),
    path("stripe/return/", stripe_return_page.as_view(), name="stripe-return"),
]   