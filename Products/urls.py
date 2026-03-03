from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductCreateView.as_view(), name='product-detail'),
    path('categories/products/<slug:slug>/', SingleCategoryProductsView.as_view(),name='category-products'),
    path('explore/', ExploreView.as_view(), name='explore'),
]