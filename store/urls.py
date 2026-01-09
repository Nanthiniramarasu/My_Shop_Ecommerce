from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Product and Cart
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout and Payment
    path('checkout/', views.checkout, name='checkout'),
    path('fake-payment/', views.fake_payment, name='fake_payment'),

    # Orders
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),

    # Product Filters
    path('products/', views.product_list, name='product_list'),
    path('category/<str:category>/', views.category_view, name='category_view'),
]
