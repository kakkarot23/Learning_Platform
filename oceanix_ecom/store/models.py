"""Models for the store app."""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        """Calculate total price of items in cart."""
        return sum(item.get_total_price() for item in self.cartitem_set.all())

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
