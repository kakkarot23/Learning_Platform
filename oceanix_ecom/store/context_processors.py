"""Context processors for store app."""
from .models import Cart, Category


def cart_context(request):
    """Add cart item count and categories to all templates."""
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.get_total_items()
        except Cart.DoesNotExist:
            pass
    return {
        'cart_count': cart_count,
        'categories': Category.objects.all(),
    }
