# OCEANIX

**E-commerce web portal for everyday essentials** — built with Django, featuring an Amazon/Flipkart-style storefront, shopping cart, multi-payment checkout, and a custom Admin Lite panel.

## Quick Start

```bash
cd oceanix_ecom
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py load_sample_products
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Storefront (shop) |
| http://127.0.0.1:8000/panel/ | **Admin Lite Panel** (staff only) |
| http://127.0.0.1:8000/admin/ | Django Admin (full backend) |

## Features

### Storefront (Customer)
- Flipkart/Amazon-inspired UI with category navigation
- Product search, ratings, MRP/discount display
- Detailed product pages with description, highlights, and payment info tabs
- Shopping cart with quantity management
- Checkout with **5 payment options**: COD, UPI, Card, Net Banking, Wallet
- Order history and confirmation

### Admin Lite Panel (`/panel/`)
- Dashboard with sales stats, recent orders, low-stock alerts
- **Product CRUD**: Add, edit, delete products with images
- Order management with status updates
- Staff-only access (set `is_staff=True` on your user)

### Django Admin (`/admin/`)
- Full database management for products, orders, carts, categories

## Project Structure

```
oceanix_ecom/
├── oceanix/          # Django project settings
├── store/            # Main app
│   ├── models.py     # Product, Category, Cart, Order
│   ├── views.py      # Storefront + Admin Lite views
│   ├── templates/    # HTML templates
│   │   └── store/admin/  # Admin Lite panel templates
│   ├── static/css/   # style.css + admin.css
│   └── management/commands/load_sample_products.py
├── manage.py
└── requirements.txt
```

## Admin Setup

After creating a superuser, you automatically get staff access:

```bash
python manage.py createsuperuser
```

Login at `/panel/` or `/admin/` with those credentials.

## Payment Methods

| Method | Description |
|--------|-------------|
| Cash on Delivery | Pay when product is delivered |
| UPI | GPay, PhonePe, Paytm |
| Credit/Debit Card | Visa, Mastercard, RuPay |
| Net Banking | All major Indian banks |
| Wallet | Paytm, PhonePe wallet |

> Payment gateway integration (Razorpay/Stripe) can be added for live transactions.

## Documentation

- [oceanix_ecom/README.md](oceanix_ecom/README.md) — Full technical documentation
- [oceanix_ecom/SETUP_GUIDE.txt](oceanix_ecom/SETUP_GUIDE.txt) — Step-by-step setup
- [oceanix_ecom/FEATURES.md](oceanix_ecom/FEATURES.md) — Feature list

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (production: PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, Font Awesome
- **Images**: Pillow

## License

MIT License
