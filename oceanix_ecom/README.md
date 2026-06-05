# OCEANIX E-Commerce Platform

A complete Django e-commerce solution with a marketplace-style storefront and a custom Admin Lite panel.

## URLs

| Path | Access | Description |
|------|--------|-------------|
| `/` | Public | Home — browse & search products |
| `/product/<id>/` | Public | Product detail with tabs |
| `/cart/` | Login | Shopping cart |
| `/checkout/` | Login | Checkout with payment options |
| `/panel/` | Staff | Admin Lite dashboard |
| `/panel/products/` | Staff | Manage products |
| `/panel/orders/` | Staff | Manage orders |
| `/admin/` | Staff | Django Admin |

## Admin Lite Panel

The Admin Lite panel at `/panel/` provides a clean, modern interface for:

1. **Dashboard** — Product count, order stats, revenue, low-stock alerts
2. **Products** — List, search, add, edit, delete with full product fields
3. **Orders** — View orders, filter by status, update order/payment status

### Product Fields

| Field | Description |
|-------|-------------|
| name | Product title |
| short_description | One-line summary for cards |
| description | Full product description |
| highlights | Bullet points (one per line) |
| price | Selling price |
| mrp | Maximum retail price (shows discount) |
| discount_percent | Manual discount badge |
| rating / review_count | Star rating display |
| category | Product category |
| stock | Inventory count |
| image | Product photo |
| is_active | Visibility toggle |

## Payment Options at Checkout

- Cash on Delivery (COD)
- UPI (GPay / PhonePe / Paytm)
- Credit / Debit Card
- Net Banking
- Wallet

COD orders are marked `payment_status=pending`; online methods are marked `completed`.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py load_sample_products
python manage.py runserver
```

## Sample Data

`load_sample_products` creates 4 categories and 6 sample products with MRP, ratings, and highlights.

## Models

- **Category** — name, slug, icon
- **Product** — full catalog with pricing, ratings, images
- **Cart / CartItem** — per-user shopping cart
- **Order / OrderItem** — orders with payment method and status tracking

## Security (Production)

1. Change `SECRET_KEY` in `oceanix/settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use PostgreSQL
5. Enable HTTPS
6. Integrate real payment gateway (Razorpay recommended for India)

## Support

- Django docs: https://docs.djangoproject.com/
- Pillow docs: https://python-pillow.org/
