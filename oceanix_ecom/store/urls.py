"""URL configuration for store app."""
from django.urls import path
from . import views

urlpatterns = [
    # Storefront
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', views.remove_coupon, name='remove_coupon'),
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
    path('developer/', views.developer_redirect, name='developer'),
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    path('notification-signup/', views.notification_signup, name='notification_signup'),

    # Phase 1: User Management Enhancements
    path('my-account/', views.user_dashboard, name='user_dashboard'),
    path('my-account/profile/', views.user_profile, name='user_profile'),
    path('my-account/addresses/', views.user_addresses, name='user_addresses'),
    path('my-account/wishlist/', views.user_wishlist, name='user_wishlist'),
    path('my-account/wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('my-account/wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Product CRUD (staff only, accessible from admin panel)
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # Admin Lite Panel
    path('panel/login/', views.admin_login_view, name='admin_login'),
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/products/', views.admin_product_list, name='admin_product_list'),
    path('panel/inventory/', views.admin_inventory, name='admin_inventory'),
    path('panel/inventory/export/', views.admin_inventory_export, name='admin_inventory_export'),
    path('panel/inventory/update/<int:pk>/', views.admin_inventory_update, name='admin_inventory_update'),
    path('panel/inventory/auto-tag/<int:pk>/', views.admin_auto_tag_api, name='admin_auto_tag_api'),
    path('panel/inventory/bulk-reorder/', views.admin_bulk_reorder_api, name='admin_bulk_reorder_api'),
    path('panel/orders/', views.admin_order_list, name='admin_order_list'),
    path('panel/orders/<int:pk>/', views.admin_order_detail, name='admin_order_detail'),
    path('panel/orders/<int:pk>/bill/', views.admin_order_bill, name='admin_order_bill'),
    path('order/<int:order_id>/return/', views.order_return_request, name='order_return_request'),
    path('seller-panel/', views.seller_panel, name='seller_panel'),
    path('subscriptions/', views.subscriptions_dashboard, name='subscriptions_dashboard'),
]
