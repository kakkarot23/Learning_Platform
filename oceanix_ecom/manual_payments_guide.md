# Manual Payments Guide (Bank Transfer & QR Codes)

If you are setting up offline or manual payments (e.g., direct Bank Transfers, NEFT/RTGS, or displaying a static UPI QR code for users to scan), you need to present your business banking details to the customer during the checkout process.

## Where to Add the Details

### 1. In the Checkout Template

You will need to modify the `checkout.html` file to display your banking information when the user selects a manual payment method.

**File Location:** `d:\OCEANIX\oceanix_ecom\store\templates\store\checkout.html`

Currently, there are payment panels defined in this file (e.g., `<div class="payment-panel" id="panel-cod">`). You can create a new payment panel for Manual Payments, or replace an existing one (like Net Banking if you are doing it manually).

**Example Code to Add to `checkout.html`:**

```html
<!-- ── MANUAL PAYMENT / BANK TRANSFER PANEL ── -->
<div class="payment-panel" id="panel-bank-transfer">
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:20px;">
        <h4 style="color:var(--primary-dark); margin-bottom:15px;"><i class="fas fa-university"></i> Bank Account Details</h4>
        <p>Please transfer the total amount to the following bank account. Your order will be processed once the funds have cleared in our account.</p>
        
        <table style="width:100%; margin-top:15px; font-size:14px;">
            <tr>
                <td style="padding:5px 0; color:#64748b;">Bank Name:</td>
                <td style="font-weight:600;">HDFC Bank</td>
            </tr>
            <tr>
                <td style="padding:5px 0; color:#64748b;">Account Name:</td>
                <td style="font-weight:600;">OCEANIX Enterprises</td>
            </tr>
            <tr>
                <td style="padding:5px 0; color:#64748b;">Account Number:</td>
                <td style="font-weight:600;">50100XXXXXXX123</td>
            </tr>
            <tr>
                <td style="padding:5px 0; color:#64748b;">IFSC Code:</td>
                <td style="font-weight:600;">HDFC0001234</td>
            </tr>
            <tr>
                <td style="padding:5px 0; color:#64748b;">Branch:</td>
                <td style="font-weight:600;">Mumbai Main Branch</td>
            </tr>
        </table>
        
        <hr style="margin:20px 0; border:none; border-top:1px dashed #cbd5e1;">
        
        <h4 style="color:var(--primary-dark); margin-bottom:15px;"><i class="fas fa-qrcode"></i> Scan to Pay via UPI</h4>
        <div style="display:flex; gap:20px; align-items:center;">
            <!-- REPLACE THIS SRC WITH YOUR ACTUAL QR CODE IMAGE IN THE STATIC FOLDER -->
            <img src="{% static 'images/payment-qr-code.png' %}" alt="UPI QR Code" style="width:120px; height:120px; border:2px solid #e2e8f0; border-radius:8px;">
            <div>
                <p style="margin:0; font-size:14px; color:#475569;">Scan this QR code using GPay, PhonePe, or Paytm.</p>
                <p style="margin:5px 0 0; font-size:14px;">UPI ID: <strong style="color:var(--primary-color);">oceanix@okhdfc</strong></p>
            </div>
        </div>
    </div>
</div>
```

### 2. Updating the Order Process

If a customer selects this manual method, you need to:
1. Ensure the `Order.payment_status` is set to **`pending`** in `views.py`.
2. Update the Order Confirmation page (`order_confirmation.html`) to display a reminder to the customer to complete the payment and send the transaction ID to your support team via email/WhatsApp.

**Example addition to `order_confirmation.html`:**
```html
{% if order.payment_method == 'bank_transfer' and order.payment_status == 'pending' %}
<div class="alert alert-warning mt-4">
    <h5><i class="fas fa-exclamation-triangle"></i> Payment Required</h5>
    <p>Your order has been placed, but we are waiting for your payment. Please transfer ₹{{ order.total_amount }} to our bank account or scan the QR code to pay via UPI.</p>
    <p><strong>Once paid, please email the transaction screenshot and your Order ID (#{{ order.order_number }}) to payments@oceanix.com.</strong></p>
</div>
{% endif %}
```

### Next Steps
1. Prepare your QR code image and place it in the `store/static/images/` directory.
2. Update the placeholder bank details above with your actual business account details.
3. Hook up the new panel to the checkout tabs by adding a new `tab` trigger.
