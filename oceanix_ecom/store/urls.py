"""URL configuration for store app."""
from django.urls import path
from . import views

urlpatterns = [
    # Storefront
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Product CRUD (staff only, accessible from admin panel)
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # Admin Lite Panel
    path('panel/login/', views.admin_login_view, name='admin_login'),
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/products/', views.admin_product_list, name='admin_product_list'),
    path('panel/inventory/', views.admin_inventory, name='admin_inventory'),
    path('panel/inventory/update/<int:pk>/', views.admin_inventory_update, name='admin_inventory_update'),
    path('panel/orders/', views.admin_order_list, name='admin_order_list'),
    path('panel/orders/<int:pk>/', views.admin_order_detail, name='admin_order_detail'),
    path('panel/orders/<int:pk>/bill/', views.admin_order_bill, name='admin_order_bill'),
]
