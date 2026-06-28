# Razorpay End-to-End Payment Integration Guide

This document details the configuration, implementation, and flow of the Razorpay payment gateway integration for the OCEANIX e-commerce platform.

## 1. Prerequisites

Before the integration can go live, you must set up your Razorpay account and install the necessary dependencies.

### Installation
Run the following command in your virtual environment to install the official Razorpay Python SDK:
```bash
pip install razorpay
```

### Razorpay Dashboard Setup
1. Log in to the [Razorpay Dashboard](https://dashboard.razorpay.com/).
2. Navigate to **Settings > API Keys**.
3. Generate a new key pair for **Test
Add your Razorpay credentials to `oceanix/settings.py` (or load them via `.env`):

```python
# Razorpay Settings
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_KEY_SECRET```

## 3. Database Updates (`models.py`)

The `Order` model must be updated to store Razorpay's generated IDs. This allows us to verify payments and process refunds later.

```python
# In store/models.py
class Order(models.Model):
    # ... existing fields ...
    
    # Razorpay Fields
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)
```
*Run `python manage.py makemigrations` and `python manage.py migrate` after adding these fields.*

## 4. Backend Logic (`views.py`)

### Initializing the Payment
When the user clicks "Place Order" using an online payment method, we create a Razorpay order before rendering the checkout page, or via an AJAX call.

```python
import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Inside checkout view when placing an order:
razorpay_order = client.order.create({
    "amount": int(order.total_amount * 100), # Amount in paise (multiply by 100)
    "currency": "INR",
    "receipt": order.order_number,
    "payment_capture": "1" # Auto-capture
})

order.razorpay_order_id = razorpay_order['id']
order.save()
```

### Verifying the Callback
Create a callback view to handle Razorpay's POST request after a successful payment.

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            # Verify the signature using the SDK
            client.utility.verify_payment_signature(params_dict)
            
            # Update the order status
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.payment_status = 'completed'
            order.save()
            
            return render(request, 'store/payment_success.html')
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'store/payment_failed.html')
```

## 5. Frontend Integration (`checkout.html`)

Include the Razorpay checkout script and trigger it when the user places an order.

```html
<!-- Include Razorpay Checkout JS -->
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

<script>
var options = {
    "key": "{{ RAZORPAY_KEY_ID }}", // Enter the Key ID generated from the Dashboard
    "amount": "{{ razorpay_amount }}", // Amount is in currency subunits (paise)
    "currency": "INR",
    "name": "OCEANIX",
    "description": "Purchase Description",
    "image": "https://example.com/your_logo",
    "order_id": "{{ razorpay_order_id }}", // The Order ID created in the backend
    "callback_url": "{% url 'payment_callback' %}", // Where razorpay will POST on success
    "prefill": {
        "name": "{{ request.user.first_name }}",
        "email": "{{ request.user.email }}",
        "contact": "{{ request.user.profile.phone }}"
    },
    "theme": {
        "color": "#3399cc"
    }
};
var rzp1 = new Razorpay(options);

document.getElementById('placeOrderBtn').onclick = function(e){
    // If online payment is selected, prevent form submit and open Razorpay
    var method = document.getElementById('selectedPaymentMethod').value;
    if(method !== 'cod') {
        e.preventDefault();
        rzp1.open();
    }
}
</script>
```

## 6. Testing the Flow
1. Use Razorpay's **Test Cards** to simulate successful and failed payments.
2. Verify that the user is correctly redirected to the success/failure pages.
3. Check your database to ensure `razorpay_payment_id` is successfully logged.
