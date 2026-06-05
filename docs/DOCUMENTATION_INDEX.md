# OCEANIX — Documentation Index

All project documentation in one place.

**Repository:** [https://github.com/kakkarot23/Oceanix](https://github.com/kakkarot23/Oceanix)

---

## Start Here

| Document | Description |
|----------|-------------|
| [../README.md](../README.md) | Project overview and quick start |
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | **Full setup commands and implementation steps** |
| [PROJECT_FLOWCHARTS.md](PROJECT_FLOWCHARTS.md) | **All system flowcharts (Mermaid diagrams)** |

---

## Setup & Commands

| Document | Location | Description |
|----------|----------|-------------|
| Implementation Guide | `docs/IMPLEMENTATION_GUIDE.md` | Complete command reference |
| Setup Guide | `oceanix_ecom/SETUP_GUIDE.txt` | Step-by-step text guide |
| Quick Start | `oceanix_ecom/QUICKSTART.txt` | Fast setup instructions |
| Start Here | `oceanix_ecom/START_HERE.txt` | New user orientation |
| Setup Scripts | `oceanix_ecom/setup.bat` / `setup.sh` | Automated setup |

### Essential Commands

```bash
cd oceanix_ecom
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_initial_data
python manage.py runserver
```

**Login:** `admin` / `admin` at http://127.0.0.1:8000/panel/

---

## Technical Documentation

| Document | Location | Description |
|----------|----------|-------------|
| Technical README | `oceanix_ecom/README.md` | Models, URLs, admin features |
| Features List | `oceanix_ecom/FEATURES.md` | All platform features |
| File Structure | `oceanix_ecom/FILE_STRUCTURE.txt` | Project file layout |
| Product Management | `oceanix_ecom/PRODUCT_MANAGEMENT_GUIDE.md` | Product CRUD guide |
| Product Quickstart | `oceanix_ecom/PRODUCT_MANAGEMENT_QUICKSTART.md` | Quick product guide |

---

## Flowcharts

| Diagram | File | Covers |
|---------|------|--------|
| Setup Flow | `docs/IMPLEMENTATION_GUIDE.md` | Installation steps |
| Shopping Flow | `docs/PROJECT_FLOWCHARTS.md` | Customer journey |
| Checkout Flow | `docs/PROJECT_FLOWCHARTS.md` | Payment process |
| Admin Flow | `docs/PROJECT_FLOWCHARTS.md` | Product & order management |
| Architecture | `docs/IMPLEMENTATION_GUIDE.md` | System design |
| Database ER | `docs/IMPLEMENTATION_GUIDE.md` | Model relationships |
| Order Lifecycle | `docs/PROJECT_FLOWCHARTS.md` | Order status states |

---

## URL Reference

### Storefront (Public)

| URL | Name |
|-----|------|
| `/` | Home |
| `/product/<id>/` | Product detail |
| `/login/` | Login |
| `/register/` | Register |
| `/about/` | About |
| `/contact/` | Contact |

### Customer (Login Required)

| URL | Name |
|-----|------|
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout |
| `/order-history/` | Order history |
| `/order-confirmation/<id>/` | Order confirmation |

### Admin Lite (Staff Required)

| URL | Name |
|-----|------|
| `/panel/` | Dashboard |
| `/panel/products/` | Product list |
| `/panel/orders/` | Order list |
| `/panel/orders/<id>/` | Order detail |
| `/product/add/` | Add product |
| `/product/<id>/edit/` | Edit product |
| `/product/<id>/delete/` | Delete product |

### Django Admin

| URL | Name |
|-----|------|
| `/admin/` | Full Django admin |

---

## Management Commands

| Command | Purpose |
|---------|---------|
| `setup_initial_data` | Create admin user + load media products |
| `load_sample_products` | Load text sample products |
| `migrate` | Apply database migrations |
| `createsuperuser` | Create additional admin |
| `runserver` | Start dev server |
| `collectstatic` | Collect static files (production) |

---

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin` |

> Change the password before deploying to production.
