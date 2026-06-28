"""Admin configuration for store app."""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, Cart, CartItem, Order, OrderItem,
    UserProfile, Address, Wishlist, ProductReview,
    ProductAttribute, ProductVariant, Coupon, NotificationSignup
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for categories."""
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for products."""
    list_display = ['name', 'category', 'sku', 'price', 'stock', 'is_active', 'is_featured', 'is_new_arrival', 'is_trending', 'is_best_seller', 'image_preview']
    list_filter = ['is_active', 'category', 'is_featured', 'is_new_arrival', 'is_trending', 'is_best_seller', 'created_at']
    search_fields = ['name', 'description', 'short_description', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'sku', 'barcode', 'short_description', 'description', 'highlights')
        }),
        ('Feature Flags', {
            'fields': ('is_featured', 'is_new_arrival', 'is_trending', 'is_best_seller', 'is_combo', 'is_flash_sale', 'flash_sale_price')
        }),
        ('Pricing', {
            'fields': ('price', 'mrp', 'discount_percent')
        }),
        ('Ratings & Media', {
            'fields': ('rating', 'review_count', 'image', 'image_preview_large', 'video_url', 'three_sixty_images')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:4px;object-fit:cover;" />',
                obj.image.url
            )
        return 'No image'
    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;border-radius:8px;" />',
                obj.image.url
            )
        return 'No image uploaded'
    image_preview_large.short_description = 'Image Preview'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders."""
    list_display = [
        'order_number', 'user', 'total_amount', 'payment_method',
        'status', 'payment_status', 'return_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'return_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'payment_status', 'return_status', 'return_reason')
        }),
        ('Shipping & Delivery', {
            'fields': ('carrier', 'tracking_number', 'delivery_slot', 'gift_wrapping', 'gift_message')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Order Total', {
            'fields': ('total_amount',)
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_total_items', 'get_total_price', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'

    def get_total_price(self, obj):
        return f'₹{obj.get_total_price()}'
    get_total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'get_total_price']
    list_filter = ['added_at']
    search_fields = ['product__name', 'cart__user__username']
    readonly_fields = ['added_at']

    def get_total_price(self, obj):
        return f'₹{obj.get_total_price()}'
    get_total_price.short_description = 'Total Price'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'gender', 'loyalty_points', 'wallet_balance', 'two_factor_enabled']
    search_fields = ['user__username', 'phone_number']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone_number', 'city', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default']
    search_fields = ['user__username', 'full_name', 'city']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase']
    search_fields = ['product__name', 'user__username', 'title', 'review']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'value']
    list_filter = ['name']
    search_fields = ['product__name', 'name', 'value']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price_adjustment', 'stock', 'is_active']
    list_filter = ['is_active']
    search_fields = ['product__name', 'sku']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'discount_amount', 'valid_from', 'valid_to', 'is_active', 'uses']
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['code']


@admin.register(NotificationSignup)
class NotificationSignupAdmin(admin.ModelAdmin):
    list_display = ['email', 'whatsapp_number', 'created_at']
    search_fields = ['email', 'whatsapp_number']
