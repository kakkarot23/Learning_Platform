"""Models for the store app."""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    """Product category."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='fa-box', help_text='Font Awesome icon class')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Product(models.Model):
    """Product model for e-commerce store."""
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products'
    )
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    highlights = models.TextField(
        blank=True,
        help_text='Enter one highlight per line (shown as bullet points)'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    mrp = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        null=True, blank=True, help_text='Maximum retail price (for showing discount)'
    )
    discount_percent = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(99)]
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, default=4.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text='Stock Keeping Unit')
    barcode = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text='Barcode code')
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_combo = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    flash_sale_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    video_url = models.URLField(blank=True, null=True, help_text="Product video link")
    three_sixty_images = models.TextField(blank=True, help_text="Comma-separated image URLs for 360 view")
    ai_tags = models.CharField(max_length=255, default='', blank=True, help_text="AI auto-detected tags (comma-separated)")
    dimensions = models.CharField(max_length=100, blank=True, help_text="e.g. 10x5x15 cm")
    weight = models.CharField(max_length=50, blank=True, help_text="e.g. 500g")
    fabric_material = models.CharField(max_length=100, blank=True, help_text="e.g. Stainless Steel, Cotton")
    warranty_info = models.CharField(max_length=100, blank=True, help_text="e.g. 1 Year Brand Warranty")
    country_of_origin = models.CharField(max_length=100, default="India")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_display_mrp(self):
        """Return MRP for display, falling back to price if not set."""
        return self.mrp if self.mrp and self.mrp > self.price else None

    def get_discount_percent(self):
        """Calculate discount percentage from MRP and price."""
        mrp = self.get_display_mrp()
        if mrp and mrp > self.price:
            return int(((mrp - self.price) / mrp) * 100)
        return self.discount_percent

    def get_highlights_list(self):
        """Return highlights as a list of strings."""
        if not self.highlights:
            return []
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Products'


class Cart(models.Model):
    """Shopping cart model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    applied_coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        """Calculate total price of items in cart."""
        return sum(item.get_total_price() for item in self.cartitem_set.all())
        
    def get_discount_amount(self):
        """Calculate discount amount from applied coupon."""
        if not self.applied_coupon or not self.applied_coupon.is_valid():
            return Decimal('0.00')
            
        subtotal = self.get_total_price()
        if subtotal < self.applied_coupon.min_purchase_amount:
            return Decimal('0.00')
            
        if self.applied_coupon.discount_amount:
            return min(subtotal, self.applied_coupon.discount_amount)
        elif self.applied_coupon.discount_percent:
            return (subtotal * self.applied_coupon.discount_percent / Decimal('100.00')).quantize(Decimal('0.01'))
        
        return Decimal('0.00')

    def get_final_price(self):
        """Calculate final price after discount."""
        return max(Decimal('0.00'), self.get_total_price() - self.get_discount_amount())

    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.cartitem_set.all())


class CartItem(models.Model):
    """Items in shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        """Calculate total price for this cart item."""
        return self.product.price * self.quantity


class Order(models.Model):
    """Order model."""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI (GPay / PhonePe / Paytm)'),
        ('card', 'Credit / Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')

    notes = models.TextField(blank=True)
    return_status_choices = [
        ('none', 'None'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('refunded', 'Refunded'),
        ('rejected', 'Rejected')
    ]
    return_status = models.CharField(max_length=20, choices=return_status_choices, default='none')
    return_reason = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    delivery_slot = models.CharField(max_length=100, blank=True)
    gift_message = models.TextField(blank=True)
    gift_wrapping = models.BooleanField(default=False)
    is_b2b = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    company_gstin = models.CharField(max_length=50, blank=True)
    is_subscription = models.BooleanField(default=False)
    subscription_period = models.CharField(max_length=50, blank=True, help_text="monthly or annual")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    def get_payment_method_display_short(self):
        """Short label for payment method."""
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        """Calculate total price for this order item."""
        return self.price * self.quantity


# --- Phase 1: User Management Enhancements ---

class UserProfile(models.Model):
    """Extended user profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Prefer not to say')]
    gender = models.CharField(max_length=1, choices=gender_choices, default='N')
    loyalty_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    two_factor_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=16, blank=True, null=True)
    preferences_json = models.TextField(default='{}', blank=True, help_text="AI Personal Shopper preferences (JSON format)")
    biometric_enabled = models.BooleanField(default=False)
    saved_cards_json = models.TextField(default='[]', blank=True, help_text="Saved cards details (JSON format)")
    saved_upi_json = models.TextField(default='[]', blank=True, help_text="Saved UPI IDs (JSON format)")
    activity_log_json = models.TextField(default='[]', blank=True, help_text="User activity logs (JSON format)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Address(models.Model):
    """User address management."""
    ADDRESS_TYPE_CHOICES = [('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='Home')
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.address_type})"
        
    def save(self, *args, **kwargs):
        if self.is_default:
            # Set other addresses to non-default
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """User wishlist."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlisted_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


# --- Phase 1: Product Enhancements ---

class ProductReview(models.Model):
    """Review and rating for a product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    review = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


class ProductAttribute(models.Model):
    """e.g. Size, Color, Material"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=50) # e.g. "Color"
    value = models.CharField(max_length=50) # e.g. "Red"

    class Meta:
        unique_together = ('product', 'name', 'value')

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"


class ProductVariant(models.Model):
    """Specific variant of a product (e.g. Red, XL)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attributes = models.ManyToManyField(ProductAttribute)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Added/Subtracted from base price")
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} Variant ({self.id})"

    def get_price(self):
        return self.product.price + self.price_adjustment


# --- Phase 1: Order & Checkout Enhancements ---

class Coupon(models.Model):
    """Discount coupons."""
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_uses = models.IntegerField(default=100)
    uses = models.IntegerField(default=0)

    def __str__(self):
        return self.code
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to and self.uses < self.max_uses


class NotificationSignup(models.Model):
    """Waitlist/Notification signups for upcoming products."""
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.whatsapp_number}"

