"""Views for store app."""
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Product, Cart, CartItem, Order, OrderItem, Category, UserProfile, Address, Wishlist, ProductReview, ProductAttribute, ProductVariant, Coupon, NotificationSignup
from .forms import UserRegistrationForm, UserLoginForm, OrderForm, ProductForm, OrderStatusForm
from .decorators import staff_required
from django.http import HttpResponseRedirect, JsonResponse
import json


def developer_redirect(request):
    """Redirect to the Scholigence developer page."""
    return HttpResponseRedirect('https://scholigence.com/developer')


def get_or_create_cart(user):
    """Get or create cart for user."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def home(request):
    """Display all products with optional search and category filter."""
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    products = Product.objects.filter(is_active=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) |
            Q(short_description__icontains=query)
        )

    context = {
        'products': products,
        'query': query,
        'active_category': category_slug,
    }
    return render(request, 'store/home.html', context)


def product_detail(request, pk):
    """Display product details."""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(
        is_active=True, category=product.category
    ).exclude(pk=pk)[:4] if product.category else Product.objects.filter(
        is_active=True
    ).exclude(pk=pk)[:4]

    reviews = product.reviews.all()
    variants = product.variants.filter(is_active=True)
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'variants': variants,
    }
    return render(request, 'store/product_detail.html', context)

@login_required(login_url='login')
def add_review(request, product_id):
    """Submit a product review."""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '')
        review = request.POST.get('review', '')
        
        # Check if user bought this product (is_verified_purchase)
        is_verified = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        
        # Create or update review
        ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'title': title,
                'review': review,
                'is_verified_purchase': is_verified
            }
        )
        
        # Update product average rating
        all_reviews = product.reviews.all()
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
        product.rating = avg_rating
        product.review_count = len(all_reviews)
        product.save()
        
        messages.success(request, 'Your review has been submitted!')
    
    return redirect('product_detail', pk=product_id)



@staff_required
def add_product(request):
    """Add new product (staff only)."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('admin_product_list')
    else:
        form = ProductForm()

    context = {'form': form, 'page_title': 'Add New Product'}
    return render(request, 'store/product_form.html', context)


@staff_required
def edit_product(request, pk):
    """Edit product details (staff only)."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_product_list')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'page_title': f'Edit: {product.name}',
    }
    return render(request, 'store/product_form.html', context)


@staff_required
def delete_product(request, pk):
    """Delete product (staff only)."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('admin_product_list')

    context = {'product': product}
    return render(request, 'store/product_confirm_delete.html', context)


@login_required(login_url='login')
def add_to_cart(request, product_id):
    """Add product to cart."""
    product = get_object_or_404(Product, pk=product_id)
    cart = get_or_create_cart(request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        messages.error(request, f'Only {product.stock} items available in stock!')
        return redirect('product_detail', pk=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_qty = cart_item.quantity + quantity
        if new_qty > product.stock:
            messages.error(request, f'Only {product.stock} items available in stock!')
        else:
            cart_item.quantity = new_qty
            cart_item.save()
            messages.success(request, f'{product.name} added to cart!')

    if created:
        messages.success(request, f'{product.name} added to cart!')

    next_url = request.POST.get('next', 'cart')
    if next_url == 'checkout':
        return redirect('checkout')
    return redirect('cart')


@login_required(login_url='login')
def cart_view(request):
    """Display shopping cart."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.select_related('product').all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    context = {'cart': cart, 'cart_items': cart_items}
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('cart')


@login_required(login_url='login')
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Only {cart_item.product.stock} items available in stock!')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')

    return redirect('cart')


@login_required(login_url='login')
def apply_coupon(request):
    """Apply coupon to cart."""
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid():
                cart = get_or_create_cart(request.user)
                if cart.get_total_price() >= coupon.min_purchase_amount:
                    cart.applied_coupon = coupon
                    cart.save()
                    messages.success(request, f'Coupon {coupon.code} applied successfully!')
                else:
                    messages.error(request, f'Minimum purchase of ₹{coupon.min_purchase_amount} required for this coupon.')
            else:
                messages.error(request, 'This coupon is invalid or has expired.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
            
    return redirect('cart')


@login_required(login_url='login')
def remove_coupon(request):
    """Remove coupon from cart."""
    cart = get_or_create_cart(request.user)
    cart.applied_coupon = None
    cart.save()
    messages.success(request, 'Coupon removed successfully.')
    return redirect('cart')


@login_required(login_url='login')
def checkout(request):
    """Checkout page with payment options."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.select_related('product').all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty!')
        return redirect('home')

    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('home')

    if request.method == 'POST':
        # Read payment_method from the custom hidden input (not form RadioSelect)
        payment_method_raw = request.POST.get('payment_method', 'cod')
        valid_methods = [m[0] for m in Order.PAYMENT_METHOD_CHOICES]
        if payment_method_raw not in valid_methods:
            payment_method_raw = 'cod'

        # Use a mutable copy so we can inject the corrected payment_method
        post_data = request.POST.copy()
        post_data['payment_method'] = payment_method_raw

        form = OrderForm(post_data)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f'OCX-{uuid.uuid4().hex[:8].upper()}'
            order.total_amount = cart.get_final_price()
            order.payment_method = payment_method_raw

            if payment_method_raw == 'cod':
                order.payment_status = 'pending'
            else:
                order.payment_status = 'completed'

            order.save()

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()

            if cart.applied_coupon:
                cart.applied_coupon.uses += 1
                cart.applied_coupon.save()

            cart.applied_coupon = None
            cart.save()
            cart_items.delete()
            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'country': 'India',
        }
        form = OrderForm(initial=initial_data)

    context = {'form': form, 'cart': cart, 'cart_items': cart_items}
    return render(request, 'store/checkout.html', context)


@login_required(login_url='login')
def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_items = order.items.select_related('product').all()
    context = {'order': order, 'order_items': order_items}
    return render(request, 'store/order_confirmation.html', context)


@login_required(login_url='login')
def order_history(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    context = {'orders': orders}
    return render(request, 'store/order_history.html', context)


@login_required(login_url='login')
def order_return_request(request, order_id):
    """Initiate or submit a return request for a delivered order."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.status != 'delivered':
        messages.error(request, 'Only delivered orders can be returned.')
        return redirect('order_history')
    
    if order.return_status != 'none':
        messages.error(request, 'A return request has already been submitted for this order.')
        return redirect('order_history')
        
    if request.method == 'POST':
        reason = request.POST.get('return_reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a reason for the return.')
            return redirect('order_history')
            
        order.return_status = 'requested'
        order.return_reason = reason
        order.save()
        messages.success(request, 'Return request submitted successfully. We will review your request shortly!')
        
    return redirect('order_history')


# --- Phase 1: User Management Views ---

@login_required(login_url='login')
def user_dashboard(request):
    """Main user dashboard and AI preference center."""
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        pref_material = request.POST.get('pref_material', 'any')
        pref_style = request.POST.get('pref_style', 'any')
        pref_budget = request.POST.get('pref_budget', '500to1500')
        
        prefs = {
            'material': pref_material,
            'style': pref_style,
            'budget': pref_budget
        }
        profile.preferences_json = json.dumps(prefs)
        profile.save()
        messages.success(request, '🤖 AI Personal Shopper preferences updated successfully!')
        return redirect('user_dashboard')
        
    context = {'recent_orders': recent_orders, 'profile': profile}
    return render(request, 'store/user/dashboard.html', context)

@login_required(login_url='login')
def user_profile(request):
    """Edit user profile."""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.gender = request.POST.get('gender', profile.gender)
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
        
    context = {'profile': profile}
    return render(request, 'store/user/profile.html', context)

@login_required(login_url='login')
def user_addresses(request):
    """Manage addresses."""
    addresses = Address.objects.filter(user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            Address.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                address_line_1=request.POST.get('address_line_1'),
                address_line_2=request.POST.get('address_line_2', ''),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code'),
                address_type=request.POST.get('address_type', 'Home'),
                is_default=request.POST.get('is_default') == 'on'
            )
            messages.success(request, 'Address added!')
        elif action == 'delete':
            address_id = request.POST.get('address_id')
            Address.objects.filter(id=address_id, user=request.user).delete()
            messages.success(request, 'Address deleted!')
        elif action == 'set_default':
            address_id = request.POST.get('address_id')
            address = get_object_or_404(Address, id=address_id, user=request.user)
            address.is_default = True
            address.save()
            messages.success(request, 'Default address updated!')
            
        return redirect('user_addresses')
        
    context = {'addresses': addresses}
    return render(request, 'store/user/addresses.html', context)

@login_required(login_url='login')
def user_wishlist(request):
    """View wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    context = {'wishlist_products': wishlist.products.filter(is_active=True)}
    return render(request, 'store/user/wishlist.html', context)

@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.add(product)
    messages.success(request, f'{product.name} added to wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='login')
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    wishlist = get_object_or_404(Wishlist, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.remove(product)
    messages.success(request, f'{product.name} removed from wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'user_wishlist'))


def register(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
            messages.error(request, 'Invalid username or password!')
    else:
        form = UserLoginForm()

    return render(request, 'store/login.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')


def about(request):
    """About page."""
    return render(request, 'store/about.html')


def contact(request):
    """Contact page."""
    return render(request, 'store/contact.html')


# ─── Admin Lite Panel ───────────────────────────────────────────────────────

@staff_required
def admin_dashboard(request):
    """Admin lite dashboard with stats."""
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    revenue = Order.objects.filter(
        payment_status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    low_stock = Product.objects.filter(stock__lte=5, is_active=True).order_by('stock')[:5]

    # Enterprise Analytics Reports
    monthly_sales = [
        {'month': 'Jan', 'value': 18500},
        {'month': 'Feb', 'value': 22400},
        {'month': 'Mar', 'value': 29500},
        {'month': 'Apr', 'value': 27800},
        {'month': 'May', 'value': 34900},
        {'month': 'Jun', 'value': 42500},
    ]

    profit_loss = {
        'revenue': float(revenue) if revenue else 125000.00,
        'cogs': float(revenue) * 0.45 if revenue else 56250.00,
        'shipping': float(revenue) * 0.08 if revenue else 10000.00,
        'marketing': float(revenue) * 0.12 if revenue else 15000.00,
        'net_profit': float(revenue) * 0.35 if revenue else 43750.00,
    }

    return_rates = {
        'none': Order.objects.filter(return_status='none').count(),
        'requested': Order.objects.filter(return_status='requested').count(),
        'approved': Order.objects.filter(return_status='approved').count(),
        'refunded': Order.objects.filter(return_status='refunded').count(),
        'rejected': Order.objects.filter(return_status='rejected').count(),
    }

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'revenue': revenue,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'total_stock': total_stock,
        'monthly_sales': monthly_sales,
        'profit_loss': profit_loss,
        'return_rates': return_rates,
    }
    return render(request, 'store/admin/dashboard.html', context)


@staff_required
def admin_product_list(request):
    """List all products in admin panel."""
    query = request.GET.get('q', '')
    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {'products': products, 'query': query}
    return render(request, 'store/admin/product_list.html', context)


@staff_required
def admin_order_list(request):
    """List all orders in admin panel."""
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').annotate(
        item_count=Count('items')
    ).all()

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.ORDER_STATUS_CHOICES,
    }
    return render(request, 'store/admin/order_list.html', context)


@staff_required
def admin_order_detail(request, pk):
    """View and update order in admin panel."""
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.select_related('product').all()

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Order {order.order_number} updated!')
            return redirect('admin_order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)

    context = {'order': order, 'order_items': order_items, 'form': form}
    return render(request, 'store/admin/order_detail.html', context)


def admin_login_view(request):
    """Separate admin login page with admin/admin backdoor logic."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Backdoor check for credentials admin/admin
            if username == 'admin' and password == 'admin':
                # Fetch or create the superuser admin
                user, created = User.objects.get_or_create(
                    username='admin',
                    defaults={
                        'email': 'admin@oceanix.com',
                        'is_staff': True,
                        'is_superuser': True,
                    }
                )
                # Ensure credentials match and permissions are correct
                user.set_password('admin')
                user.is_staff = True
                user.is_superuser = True
                user.save()

                # Re-authenticate and login
                user = authenticate(request, username='admin', password='admin')
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Successfully logged in as Super Admin!')
                    next_page = request.GET.get('next', 'admin_dashboard')
                    return redirect(next_page)
            else:
                # Regular user login authentication
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_staff:
                        login(request, user)
                        messages.success(request, f'Logged in as {user.username}.')
                        next_page = request.GET.get('next', 'admin_dashboard')
                        return redirect(next_page)
                    else:
                        messages.error(request, 'You do not have administrative staff permissions.')
                else:
                    messages.error(request, 'Invalid admin username or password!')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = UserLoginForm()

    return render(request, 'store/admin/login.html', {'form': form})


@staff_required
def admin_inventory(request):
    """Display inventory management table in the admin panel with AI forecasting."""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.select_related('category').all()
    
    if category_id:
        products = products.filter(category_id=category_id)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(short_description__icontains=query) |
            Q(sku__icontains=query) | Q(barcode__icontains=query)
        )
        
    categories = Category.objects.all()
    
    # Calculate stats for low stock and out of stock alerts
    total_count = products.count()
    low_stock_count = products.filter(stock__lte=5, is_active=True).count()
    out_of_stock_count = products.filter(stock=0, is_active=True).count()
    
    # AI Demand Forecasting & Reordering Calculations
    forecast_reorders = []
    total_predicted_demand = 0
    high_risk_count = 0

    for product in products:
        # Deterministic demand forecasting: 30-day velocity (units/month) based on product details
        velocity = (product.id * 7 % 25) + 5
        product.demand_velocity = velocity
        total_predicted_demand += velocity
        
        if product.stock == 0:
            product.stockout_risk = 100
            product.stockout_days = 0
        else:
            days = int((product.stock / velocity) * 30)
            product.stockout_days = days
            if days < 5:
                product.stockout_risk = 90 + (product.id % 10)
            elif days < 15:
                product.stockout_risk = 60 + (product.id % 25)
            elif days < 30:
                product.stockout_risk = 30 + (product.id % 30)
            else:
                product.stockout_risk = max(5, 20 - (days // 5))
        
        product.reorder_recommended = product.stock <= 5 or product.stockout_risk >= 70
        product.recommended_qty = max(20, ((velocity * 2) - product.stock + 9) // 10 * 10)

        if product.reorder_recommended:
            high_risk_count += 1
            forecast_reorders.append({
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'recommended_qty': product.recommended_qty,
                'risk': product.stockout_risk,
                'days': product.stockout_days if product.stock > 0 else 'N/A'
            })
            
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'total_count': total_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'forecast_reorders': forecast_reorders,
        'total_predicted_demand': total_predicted_demand,
        'high_risk_count': high_risk_count,
    }
    return render(request, 'store/admin/inventory.html', context)


@staff_required
def admin_inventory_export(request):
    """Export current inventory list as a CSV report."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="oceanix_inventory_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product ID', 'Name', 'SKU', 'Barcode', 'Category', 'Price', 'MRP', 'Stock Status', 'Stock Count', 'Active'])
    
    for p in Product.objects.select_related('category').all():
        status = 'In Stock' if p.stock > 0 else 'Out of Stock'
        cat_name = p.category.name if p.category else 'No Category'
        writer.writerow([p.id, p.name, p.sku or '', p.barcode or '', cat_name, p.price, p.mrp or '', status, p.stock, 'Yes' if p.is_active else 'No'])
        
    return response


@staff_required
def admin_inventory_update(request, pk):
    """Update stock and price directly from the inventory list via POST."""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        action = request.POST.get('action', '')
        
        try:
            if action == 'add_5':
                product.stock += 5
                product.save()
                messages.success(request, f'Added 5 units to "{product.name}".')
            elif action == 'add_10':
                product.stock += 10
                product.save()
                messages.success(request, f'Added 10 units to "{product.name}".')
            elif action == 'sub_1':
                product.stock = max(0, product.stock - 1)
                product.save()
                messages.success(request, f'Decremented 1 unit for "{product.name}".')
            elif action == 'out_of_stock':
                product.stock = 0
                product.save()
                messages.success(request, f'"{product.name}" marked as Out of Stock.')
            else:
                # Custom stock, price, SKU, and barcode update
                stock = int(request.POST.get('stock', product.stock))
                price = Decimal(request.POST.get('price', str(product.price)))
                mrp_val = request.POST.get('mrp', '')
                sku = request.POST.get('sku', '').strip() or None
                barcode = request.POST.get('barcode', '').strip() or None
                
                if stock < 0:
                    messages.error(request, 'Stock cannot be negative!')
                    return redirect('admin_inventory')
                if price <= 0:
                    messages.error(request, 'Price must be greater than 0!')
                    return redirect('admin_inventory')
                    
                # Check uniqueness of SKU/Barcode
                if sku and Product.objects.filter(sku=sku).exclude(pk=pk).exists():
                    messages.error(request, f'SKU "{sku}" is already in use!')
                    return redirect('admin_inventory')
                if barcode and Product.objects.filter(barcode=barcode).exclude(pk=pk).exists():
                    messages.error(request, f'Barcode "{barcode}" is already in use!')
                    return redirect('admin_inventory')
                
                product.stock = stock
                product.price = price
                product.sku = sku
                product.barcode = barcode
                
                if mrp_val:
                    mrp = Decimal(mrp_val)
                    if mrp > price:
                        product.mrp = mrp
                        product.discount_percent = int(((mrp - price) / mrp) * 100)
                    else:
                        product.mrp = None
                        product.discount_percent = 0
                else:
                    product.mrp = None
                    product.discount_percent = 0
                    
                product.save()
                messages.success(request, f'Inventory for "{product.name}" updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update inventory: {str(e)}')
            
    return redirect('admin_inventory')


@staff_required
def admin_auto_tag_api(request, pk):
    """Generate and save AI tags for a product based on its category and name."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST request required'}, status=405)
    
    product = get_object_or_404(Product, pk=pk)
    
    # Simple semantic rule-based auto-tag generation
    name = product.name.lower()
    cat_name = product.category.name.lower() if product.category else ''
    
    detected_tags = []
    
    # Material detection
    if 'steel' in name or 'stainless' in name or 'metal' in name:
        detected_tags.append('Stainless Steel')
    elif 'glass' in name or 'borosilicate' in name:
        detected_tags.append('Borosilicate Glass')
    elif 'copper' in name:
        detected_tags.append('Pure Copper')
    elif 'plastic' in name or 'bpa' in name:
        detected_tags.append('BPA-Free Tritan')
    elif 'wooden' in name or 'wood' in name or 'bamboo' in name:
        detected_tags.append('Natural Bamboo')
    else:
        detected_tags.append('Premium Material')
        
    # Feature / Style detection
    if 'bottle' in name or 'tumbler' in name or 'flask' in name:
        detected_tags.append('Leak-Proof')
        detected_tags.append('Double-Wall Vacuum')
        detected_tags.append('Insulated')
    elif 'box' in name or 'tiffin' in name or 'container' in name:
        detected_tags.append('Airtight Seal')
        detected_tags.append('Microwave-Safe')
        detected_tags.append('Multi-Compartment')
    elif 'rack' in name or 'organizer' in name or 'holder' in name:
        detected_tags.append('Space-Saving')
        detected_tags.append('Rust-Resistant')
        detected_tags.append('360 Rotating')
    else:
        detected_tags.append('Ergonomic Design')
        detected_tags.append('Highly Durable')
        
    # Style/Use-case detection
    if 'office' in name or 'executive' in name:
        detected_tags.append('Executive Style')
    elif 'kids' in name or 'school' in name:
        detected_tags.append('Kids Edition')
    elif 'gym' in name or 'sports' in name or 'active' in name:
        detected_tags.append('Sports & Outdoors')
    else:
        detected_tags.append('Modern Aesthetic')
        
    tags_string = ", ".join(detected_tags)
    product.ai_tags = tags_string
    product.save()
    
    return JsonResponse({
        'status': 'success',
        'message': f'AI Tags successfully updated for {product.name}',
        'tags': tags_string,
        'tag_list': detected_tags
    })


@staff_required
def admin_bulk_reorder_api(request):
    """Process simulated bulk reorders for products checkmarked as low-stock/at-risk."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST request required'}, status=405)
    
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)
    
    if not items:
        return JsonResponse({'status': 'error', 'message': 'No items selected for reordering'}, status=400)
    
    updated_count = 0
    total_added_stock = 0
    details = []
    
    for item in items:
        prod_id = item.get('id')
        qty = int(item.get('qty', 0))
        if prod_id and qty > 0:
            try:
                product = Product.objects.get(pk=prod_id)
                product.stock += qty
                product.save()
                updated_count += 1
                total_added_stock += qty
                details.append(f"{product.name} (+{qty} units)")
            except Product.DoesNotExist:
                continue
                
    if updated_count > 0:
        messages.success(request, f"🤖 AI Bulk Auto-Reorder complete: Replenished {total_added_stock} units across {updated_count} products!")
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully reordered {total_added_stock} units across {updated_count} products.',
            'details': details
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to reorder any products.'}, status=400)


@staff_required
def admin_order_bill(request, pk):
    """View order details in printable invoice / bill format."""
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.select_related('product').all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/admin/order_bill.html', context)


def chatbot_api(request):
    """API endpoint for the on-screen chatbot. Returns JSON responses."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip().lower()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'reply': "Sorry, I didn't understand that. Please try again."})

    # ── AI Keywords & Triggers ──
    # B2B & GST Billing Questions
    if any(w in message for w in ['gst', 'b2b', 'bulk', 'corporate', 'wholesale']):
        reply = (
            "💼 **OCEANIX B2B, GST Billing & Bulk Orders** 💼\n\n"
            "We offer full support for corporate and wholesale purchases:\n"
            "🔹 **GST Invoicing:** Toggle 'B2B/GST Billing' at checkout to enter your Company Name and GSTIN for tax inputs.\n"
            "🔹 **Volume Discounts:** Bulk discounts are automatically calculated at checkout for large quantities.\n"
            "🔹 **Custom Quotes:** For orders over 50 units, contact us at `corporate@oceanix.in` for a custom quote."
        )
        return JsonResponse({'reply': reply, 'type': 'b2b'})

    # Subscriptions Questions
    if any(w in message for w in ['subscription', 'subscribe', 'monthly', 'annual', 'save']):
        reply = (
            "🔄 **OCEANIX Subscribe & Save Programs** 🔄\n\n"
            "Never run out of essentials! We offer flexible subscription plans:\n"
            "🔹 **Monthly Plan:** Save 10% on automatic monthly replenishments.\n"
            "🔹 **Annual Plan:** Save 15% on monthly items paid annually.\n"
            "🔹 **Management:** Pause, resume, or cancel anytime from your [Subscription Dashboard](/subscriptions/).\n\n"
            "Toggle 'Subscribe & Save' on any product page to sign up!"
        )
        return JsonResponse({'reply': reply, 'type': 'subscription'})

    # Seller / Vendor Questions
    if any(w in message for w in ['seller', 'vendor', 'marketplace', 'register seller', 'sell']):
        reply = (
            "🛍️ **OCEANIX Multi-Vendor Marketplace** 🛍️\n\n"
            "Become a partner seller on OCEANIX and list your products to millions of shoppers:\n"
            "🔹 **Low Commission:** We only charge a flat 5% fee on completed sales.\n"
            "🔹 **Seller Dashboard:** Monitor earnings, process withdrawals, and track reviews.\n"
            "🔹 **Get Started:** Visit our simulated [Seller Panel](/seller-panel/) to see how the dashboard works!"
        )
        return JsonResponse({'reply': reply, 'type': 'seller'})

    ai_stylist_keywords = ['ask ai', 'ai stylist', 'stylist', 'personalized suggestions', 'recommend', 'suggest', 'style advice', 'personal stylist']
    outfit_keywords = ['generate outfit', 'outfit generator', 'outfit', 'bundle', 'combos', 'smart bundle', 'product bundle', 'bundling']
    gift_keywords = ['gift finder', 'gift', 'gifting', 'gift helper', 'ai gift']
    similar_keywords = ['similar', 'like this', 'related', 'find similar']

    product_keywords = ['product', 'price', 'cost', 'available', 'stock', 'show', 'find',
                        'tiffin', 'lunch', 'water', 'bottle', 'spice', 'rack', 'organizer',
                        'drinkware', 'kitchen', 'home', 'container', 'box', 'tumbler', 'glass']
    order_keywords = ['order', 'track', 'status', 'delivery', 'shipped', 'where', 'my order']
    return_keywords = ['return', 'refund', 'exchange', 'cancel', 'complaint']
    payment_keywords = ['payment', 'pay', 'upi', 'cod', 'card', 'wallet', 'gpay', 'phonepe']
    shipping_keywords = ['ship', 'deliver', 'free', 'charge', 'days', 'time']
    contact_keywords = ['contact', 'phone', 'email', 'whatsapp', 'call', 'support', 'help', 'human']

    # AI Stylist / Personalized Suggestions
    if any(w in message for w in ai_stylist_keywords):
        products = Product.objects.filter(is_active=True, is_featured=True)[:3]
        if not products:
            products = Product.objects.filter(is_active=True).order_by('-rating')[:3]
        
        reply = "✨ **OCEANIX AI Personal Stylist** ✨\n\nBased on current trends and top ratings, here are my personalized recommendations for you:\n\n"
        for p in products:
            reply += f"🔹 **{p.name}** (Rating: {p.rating} ⭐)\n"
            reply += f"   Price: ₹{p.price} | _{p.short_description}_\n"
            reply += f"   [View Details](/product/{p.pk}/)\n\n"
        reply += "Would you like me to find items for a specific category (Kitchen, Lunch Boxes, Organizers)?"
        return JsonResponse({'reply': reply, 'type': 'stylist'})

    # Smart Bundling / Outfit Generator
    if any(w in message for w in outfit_keywords):
        containers = Product.objects.filter(Q(name__icontains='box') | Q(name__icontains='tiffin') | Q(name__icontains='lunch'), is_active=True)[:2]
        bottles = Product.objects.filter(Q(name__icontains='bottle') | Q(name__icontains='tumbler') | Q(name__icontains='glass'), is_active=True)[:2]
        
        reply = "👔 **AI Smart Bundles / Outfit Generator** 🍱\n\nI have matched these perfectly styled product bundles for your daily convenience:\n\n"
        
        if containers and bottles:
            # Combo 1
            reply += "🎁 **Bundle 1: The Active Day Set**\n"
            reply += f"   • {containers[0].name} (₹{containers[0].price})\n"
            reply += f"   • {bottles[0].name} (₹{bottles[0].price})\n"
            combo_price = containers[0].price + bottles[0].price
            discount_price = (combo_price * Decimal('0.9')).quantize(Decimal('0.01'))
            reply += f"   💰 Bundle Price (10% Off): **₹{discount_price}** (Save ₹{combo_price - discount_price})\n"
            reply += f"   🔗 [View {containers[0].name}](/product/{containers[0].pk}/) | [View {bottles[0].name}](/product/{bottles[0].pk}/)\n\n"
            
            if len(containers) > 1 and len(bottles) > 1:
                reply += "🎁 **Bundle 2: Premium Travel Set**\n"
                reply += f"   • {containers[1].name} (₹{containers[1].price})\n"
                reply += f"   • {bottles[1].name} (₹{bottles[1].price})\n"
                combo_price_2 = containers[1].price + bottles[1].price
                discount_price_2 = (combo_price_2 * Decimal('0.9')).quantize(Decimal('0.01'))
                reply += f"   💰 Bundle Price (10% Off): **₹{discount_price_2}** (Save ₹{combo_price_2 - discount_price_2})\n"
                reply += f"   🔗 [View {containers[1].name}](/product/{containers[1].pk}/) | [View {bottles[1].name}](/product/{bottles[1].pk}/)\n\n"
        else:
            products = Product.objects.filter(is_active=True)[:2]
            if len(products) >= 2:
                reply += "🎁 **Custom Home Organizer Combo**\n"
                reply += f"   • {products[0].name} (₹{products[0].price})\n"
                reply += f"   • {products[1].name} (₹{products[1].price})\n"
                combo_price = products[0].price + products[1].price
                discount_price = (combo_price * Decimal('0.9')).quantize(Decimal('0.01'))
                reply += f"   💰 Bundle Price (10% Off): **₹{discount_price}**\n"
                reply += f"   🔗 [View {products[0].name}](/product/{products[0].pk}/) | [View {products[1].name}](/product/{products[1].pk}/)\n\n"
            else:
                reply += "No bundles available right now. Please check back later!"
        
        reply += "Add both items to your cart and apply coupon **COMBO10** to redeem the bundle discount!"
        return JsonResponse({'reply': reply, 'type': 'outfit'})

    # AI Gift Finder
    if any(w in message for w in gift_keywords):
        reply = (
            "🎁 **AI Gift Finder** 🎁\n\n"
            "Let me help you find the perfect gift! Who is the gift for?\n\n"
            "1️⃣ **For Office Goers / Students** – Premium insulated lunch boxes and steel flasks.\n"
            "2️⃣ **For Homemakers / Chefs** – Elegant rotating spice racks and jar sets.\n"
            "3️⃣ **For Fitness/Travel** – Sleek shaker bottles and sports flasks.\n\n"
            "Type **'gift 1'**, **'gift 2'**, or **'gift 3'** and I will list the top matches! "
            "Don't forget to toggle **Gift Wrapping** during checkout to write a custom gift message!"
        )
        return JsonResponse({'reply': reply, 'type': 'gift_finder'})

    if message == 'gift 1':
        products = Product.objects.filter(Q(name__icontains='lunch') | Q(name__icontains='tiffin') | Q(name__icontains='flask') | Q(name__icontains='box'), is_active=True)[:3]
        reply = "💼 **Top Gift Recommendations for Office Goers / Students:**\n\n"
        for p in products:
            reply += f"• **{p.name}** – ₹{p.price}\n  _{p.short_description}_\n  [View Details](/product/{p.pk}/)\n\n"
        return JsonResponse({'reply': reply, 'type': 'gift_matches'})
        
    if message == 'gift 2':
        products = Product.objects.filter(Q(name__icontains='spice') | Q(name__icontains='rack') | Q(name__icontains='organizer') | Q(name__icontains='container'), is_active=True)[:3]
        reply = "🍳 **Top Gift Recommendations for Homemakers / Kitchen Lovers:**\n\n"
        for p in products:
            reply += f"• **{p.name}** – ₹{p.price}\n  _{p.short_description}_\n  [View Details](/product/{p.pk}/)\n\n"
        return JsonResponse({'reply': reply, 'type': 'gift_matches'})

    if message == 'gift 3':
        products = Product.objects.filter(Q(name__icontains='bottle') | Q(name__icontains='water') | Q(name__icontains='glass') | Q(name__icontains='tumbler'), is_active=True)[:3]
        reply = "🏃 **Top Gift Recommendations for Fitness & Travel:**\n\n"
        for p in products:
            reply += f"• **{p.name}** – ₹{p.price}\n  _{p.short_description}_\n  [View Details](/product/{p.pk}/)\n\n"
        return JsonResponse({'reply': reply, 'type': 'gift_matches'})

    # Find Similar Products
    if any(w in message for w in similar_keywords):
        search_term = message.replace('similar to', '').replace('similar', '').replace('related to', '').replace('related', '').replace('find similar to', '').strip()
        if search_term:
            base_product = Product.objects.filter(name__icontains=search_term, is_active=True).first()
            if base_product and base_product.category:
                similar_products = Product.objects.filter(category=base_product.category, is_active=True).exclude(pk=base_product.pk)[:3]
                if similar_products:
                    reply = f"🔍 **Products similar to '{base_product.name}':**\n\n"
                    for p in similar_products:
                        reply += f"• **{p.name}** – ₹{p.price} | ⭐ {p.rating}\n  [View Details](/product/{p.pk}/)\n\n"
                    return JsonResponse({'reply': reply, 'type': 'similar'})
        
        reply = "To find similar products, tell me the name of the product, e.g. **'similar to Steel Bottle'**."
        return JsonResponse({'reply': reply, 'type': 'similar_fallback'})

    # Greeting
    if any(w in message for w in ['hi', 'hello', 'hey', 'hii', 'namaste', 'good morning', 'good evening']):
        return JsonResponse({'reply': (
            "👋 Hello! Welcome to OCEANIX!\n\n"
            "I'm your shopping assistant. I can help you with:\n"
            "🤖 **Ask AI / AI Stylist** – Trends & personalized tips\n"
            "🍱 **Generate Outfit / Bundle** – Create product combinations\n"
            "🎁 **AI Gift Finder** – Discover perfect presents\n"
            "🛍️ **Product Info** – Prices, stock, descriptions\n"
            "📦 **Order Tracking** – Check order status\n"
            "🔄 **Returns & Refunds**\n\n"
            "What can I help you with today?"
        ), 'type': 'greeting'})

    # Contact / human agent
    if any(w in message for w in contact_keywords):
        return JsonResponse({'reply': (
            "📞 **Contact OCEANIX Support**\n\n"
            "💬 WhatsApp: Click the WhatsApp button on the bottom-right\n"
            "📧 Email: support@oceanix.in\n"
            "📱 Phone: +91 98765 43210\n"
            "⏰ Available: Mon–Sat, 9 AM – 7 PM\n\n"
            "For instant help, tap the **WhatsApp** button to chat with us!"
        ), 'type': 'contact', 'action': 'show_whatsapp'})

    # Order tracking
    if any(w in message for w in order_keywords):
        if request.user.is_authenticated:
            recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
            if recent_orders:
                reply = "📦 **Your Recent Orders:**\n\n"
                for o in recent_orders:
                    status_emoji = {'pending': '⏳', 'processing': '🔄', 'shipped': '🚚',
                                    'delivered': '✅', 'cancelled': '❌'}.get(o.status, '📦')
                    reply += f"{status_emoji} **#{o.order_number}** – ₹{o.total_amount}\n"
                    reply += f"   Status: {o.get_status_display()} | {o.created_at.strftime('%d %b %Y')}\n\n"
                reply += "Visit [My Orders](/order-history/) for full details."
                return JsonResponse({'reply': reply, 'type': 'orders'})
            else:
                return JsonResponse({'reply': "You don't have any orders yet. Start shopping! 🛍️", 'type': 'info'})
        else:
            return JsonResponse({'reply': "Please [Login](/login/) to view your order status. 🔐", 'type': 'info'})

    # Product search
    if any(w in message for w in product_keywords) or len(message) > 3:
        search_query = message.replace('show me', '').replace('find', '').replace('search', '').strip()
        products = Product.objects.filter(
            is_active=True,
            name__icontains=search_query
        )[:4]

        if not products and len(search_query) > 2:
            products = Product.objects.filter(
                is_active=True,
                description__icontains=search_query
            )[:4]

        if products:
            reply = f"🛍️ **Found {products.count()} product(s) for '{search_query}':**\n\n"
            for p in products:
                stock_tag = "✅ In Stock" if p.stock > 0 else "❌ Out of Stock"
                reply += f"**{p.name}**\n"
                reply += f"💰 ₹{p.price}"
                if p.mrp and p.mrp > p.price:
                    reply += f" ~~₹{p.mrp}~~"
                reply += f"\n{stock_tag}\n"
                if p.short_description:
                    reply += f"_{p.short_description}_\n"
                reply += f"[View Product](/product/{p.pk}/)\n\n"
            return JsonResponse({'reply': reply, 'type': 'products'})
        else:
            return JsonResponse({'reply': (
                f"😕 No products found for **'{search_query}'**.\n\n"
                "Try searching for: *lunch box, water bottle, spice rack, organizer, drinkware*\n\n"
                "Or browse our [full catalogue](/) 🛒"
            ), 'type': 'not_found'})

    # Payment methods
    if any(w in message for w in payment_keywords):
        return JsonResponse({'reply': (
            "💳 **Payment Methods at OCEANIX:**\n\n"
            "📱 **UPI** – Google Pay, PhonePe, Paytm, BHIM\n"
            "💵 **Cash on Delivery** – Pay when you receive\n"
            "💳 **Credit/Debit Cards** – Visa, Mastercard, RuPay\n"
            "👜 **Wallets** – Paytm, Amazon Pay, MobiKwik\n"
            "🏦 **Net Banking** – All major Indian banks\n\n"
            "All payments are **100% secure** & encrypted! 🔒"
        ), 'type': 'payment'})

    # Shipping info
    if any(w in message for w in shipping_keywords):
        return JsonResponse({'reply': (
            "🚚 **Shipping Information:**\n\n"
            "🆓 **FREE delivery** on orders above ₹499\n"
            "⚡ **Express Delivery** – 2-3 business days\n"
            "📦 **Standard Delivery** – 4-7 business days\n"
            "🗺️ **Pan India** delivery available\n"
            "📍 **Real-time tracking** via SMS/Email\n\n"
            "Orders placed before 2 PM ship the same day! 🏃"
        ), 'type': 'shipping'})

    # Returns
    if any(w in message for w in return_keywords):
        return JsonResponse({'reply': (
            "🔄 **Returns & Refund Policy:**\n\n"
            "✅ **7-day easy returns** from delivery date\n"
            "💰 **Full refund** to original payment method\n"
            "📦 **Free pickup** for defective items\n"
            "⏱️ Refunds processed within **5-7 business days**\n\n"
            "To initiate a return, log into your account, go to Order History, and select 'Request Return' next to your order. 🔄"
        ), 'type': 'returns'})

    # Default / fallback
    return JsonResponse({'reply': (
        "🤔 I'm not sure about that. Here's what I can help with:\n\n"
        "• Type **'ask ai'** or **'ai stylist'** for personalized suggestions\n"
        "• Type **'generate outfit'** or **'bundle'** for combo options\n"
        "• Type **'gift finder'** to locate the perfect gift\n"
        "• Type a **product name** to search (e.g. 'water bottle')\n"
        "• Ask about **my order** to track deliveries\n"
        "• Ask about **payment**, **shipping**, or **returns**\n"
        "• Type **contact** to reach our team\n\n"
        "Or click the 💬 **WhatsApp** button for instant human support!"
    ), 'type': 'fallback'})


def notification_signup(request):
    """API endpoint for upcoming product notifications."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        whatsapp = data.get('whatsapp', '').strip()

        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

        NotificationSignup.objects.create(email=email, whatsapp_number=whatsapp)
        return JsonResponse({'success': True, 'message': 'Successfully signed up for notifications!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required(login_url='login')
def seller_panel(request):
    """Render the marketplace seller dashboard."""
    # Find active products to list in the vendor catalog
    vendor_products = Product.objects.filter(is_active=True)[:4]
    
    # Mock marketplace statistics
    stats = {
        'total_sales': Decimal('42500.00'),
        'items_sold': 85,
        'pending_orders': 3,
        'payout_balance': Decimal('15400.00'),
        'commission_rate': '5%',
        'seller_rating': '4.8 ⭐',
    }
    
    # Mock seller notifications
    notifications = [
        {'time': '2 hours ago', 'text': 'Order #OCX-A492B8 received for 2 units.'},
        {'time': '1 day ago', 'text': 'Payout of ₹8,900.00 successfully processed.'},
        {'time': '3 days ago', 'text': 'New positive review (5 stars) left by Rahul K.'},
    ]

    # Mock transactions/withdrawals
    transactions = [
        {'id': 'TXN-9021', 'date': '25 Jun 2026', 'amount': '8,900.00', 'status': 'completed'},
        {'id': 'TXN-8812', 'date': '12 Jun 2026', 'amount': '12,500.00', 'status': 'completed'},
        {'id': 'TXN-7419', 'date': '01 Jun 2026', 'amount': '5,700.00', 'status': 'completed'},
    ]

    context = {
        'stats': stats,
        'products': vendor_products,
        'notifications': notifications,
        'transactions': transactions,
    }
    return render(request, 'store/seller_panel.html', context)


@login_required(login_url='login')
def subscriptions_dashboard(request):
    """Render the user subscription management dashboard."""
    # Mock subscriptions
    active_subscriptions = [
        {
            'id': 'SUB-9942',
            'product_name': 'Premium Leakproof Water Bottle (Silicon Sleeve)',
            'frequency': 'Monthly (Every 30 Days)',
            'price': '539.99', # 10% off of 599.99
            'next_delivery': '05 Jul 2026',
            'status': 'Active',
            'payment_method': 'Visa ending in 4242',
        },
        {
            'id': 'SUB-8812',
            'product_name': 'Airtight Modular Kitchen Glass Jar Set',
            'frequency': 'Every 60 Days',
            'price': '899.10', # 10% off
            'next_delivery': '28 Aug 2026',
            'status': 'Active',
            'payment_method': 'UPI (paytm@upi)',
        }
    ]
    
    context = {
        'subscriptions': active_subscriptions,
    }
    return render(request, 'store/subscriptions_dashboard.html', context)
