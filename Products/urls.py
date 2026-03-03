from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('explore/', ExploreView.as_view(), name='explore'),
    path('explore/<int:pk>/', ProductDetailView.as_view(), name='explore-detail'),
    path('save-product/', SaveProductsView.as_view(), name='save-product'),
    path('delete-save-product/<int:pk>/', DeleteSaveProductsView.as_view(), name='delete-save-product'),
]