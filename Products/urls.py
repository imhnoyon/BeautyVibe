from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductCreateView.as_view(), name='product-detail'),
    path('explore/', ExploreView.as_view(), name='explore'),
    path('save-product/', SaveProductsView.as_view(), name='save-product'),
]