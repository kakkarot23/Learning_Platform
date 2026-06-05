"""Admin configuration for store app."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for categories."""
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for products."""
    list_display = ['name', 'category', 'price', 'mrp', 'stock', 'rating', 'is_active', 'image_preview']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'short_description', 'description', 'highlights')
        }),
        ('Pricing', {
            'fields': ('price', 'mrp', 'discount_percent')
        }),
        ('Ratings & Media', {
            'fields': ('rating', 'review_count', 'image', 'image_preview_large')
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
        'status', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'payment_status')
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
