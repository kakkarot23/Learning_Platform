# OCEANIX — Project Flowcharts

Visual diagrams for all major flows in the OCEANIX e-commerce platform.

---

## 1. System Overview

```mermaid
flowchart TB
    subgraph Users
        Customer[Customer / Shopper]
        AdminUser[Admin / Staff]
    end

    subgraph OCEANIX Platform
        Store[Storefront<br/>Amazon/Flipkart UI]
        AdminLite[Admin Lite Panel<br/>/panel/]
        DjangoAdmin[Django Admin<br/>/admin/]
    end

    subgraph Core Features
        Products[Product Catalog]
        Cart[Shopping Cart]
        Checkout[Checkout + Payments]
        Orders[Order Management]
    end

    Customer --> Store
    Customer --> Cart
    Customer --> Checkout
    AdminUser --> AdminLite
    AdminUser --> DjangoAdmin

    Store --> Products
    Cart --> Products
    Checkout --> Orders
    AdminLite --> Products
    AdminLite --> Orders
    DjangoAdmin --> Products
    DjangoAdmin --> Orders
```

---

## 2. User Registration & Authentication

```mermaid
flowchart TD
    Start([User visits site]) --> AuthCheck{Authenticated?}
    AuthCheck -->|Yes| Home[Home Page]
    AuthCheck -->|No| Choice{Action?}

    Choice -->|Register| RegForm[Fill Registration Form]
    RegForm --> RegValid{Valid?}
    RegValid -->|No| RegError[Show Errors]
    RegError --> RegForm
    RegValid -->|Yes| CreateUser[Create User Account]
    CreateUser --> LoginPage[Redirect to Login]

    Choice -->|Login| LoginForm[Enter Username + Password]
    LoginForm --> LoginValid{Credentials OK?}
    LoginValid -->|No| LoginError[Invalid credentials]
    LoginError --> LoginForm
    LoginValid -->|Yes| Session[Create Session]
    Session --> Home

    Home --> StaffCheck{is_staff?}
    StaffCheck -->|Yes| AdminLink[Show Admin Panel Link]
    StaffCheck -->|No| Shop[Shop normally]
```

---

## 3. Product Browsing & Search

```mermaid
flowchart TD
    Home[Home Page] --> Browse{User Action}

    Browse -->|Search| SearchBox[Enter search query ?q=]
    SearchBox --> FilterName[Filter by name / description]
    FilterName --> Results[Display matching products]

    Browse -->|Category| CatClick[Click category tab]
    CatClick --> FilterCat[Filter by category slug]
    FilterCat --> Results

    Browse -->|View All| AllProducts[Show all active products]

    Results --> ProductCard[Product Card]
    AllProducts --> ProductCard

    ProductCard --> Detail[Product Detail Page]
    Detail --> Tabs{Info Tab}
    Tabs --> Desc[Description]
    Tabs --> Highlights[Key Highlights]
    Tabs --> PaymentInfo[Payment & Delivery Info]
```

---

## 4. Shopping Cart Flow

```mermaid
flowchart TD
    Product[Product Detail] --> AddCart[Add to Cart POST]
    AddCart --> LoginCheck{Logged in?}
    LoginCheck -->|No| RedirectLogin[Redirect to Login]
    LoginCheck -->|Yes| GetCart[Get or Create Cart]

    GetCart --> StockCheck{Stock available?}
    StockCheck -->|No| StockError[Show stock error]
    StockCheck -->|Yes| AddItem[Add/Update CartItem]
    AddItem --> CartPage[Cart Page /cart/]

    CartPage --> CartAction{Action}
    CartAction -->|Update Qty| UpdateQty[POST update-cart-item]
    CartAction -->|Remove| RemoveItem[DELETE cart item]
    CartAction -->|Checkout| CheckoutPage[Go to Checkout]

    UpdateQty --> CartPage
    RemoveItem --> CartPage
```

---

## 5. Checkout & Payment Flow

```mermaid
flowchart TD
    Checkout[Checkout Page] --> CartEmpty{Cart has items?}
    CartEmpty -->|No| RedirectHome[Redirect to Home]
    CartEmpty -->|Yes| ShowForm[Show address form + payment options]

    ShowForm --> FillForm[Customer fills details]
    FillForm --> SelectPay{Payment Method}

    SelectPay -->|COD| COD[Cash on Delivery]
    SelectPay -->|UPI| UPI[UPI Payment]
    SelectPay -->|Card| Card[Card Payment]
    SelectPay -->|Net Banking| NB[Net Banking]
    SelectPay -->|Wallet| Wallet[Wallet]

    COD --> PlaceOrder[Place Order]
    UPI --> PlaceOrder
    Card --> PlaceOrder
    NB --> PlaceOrder
    Wallet --> PlaceOrder

    PlaceOrder --> CreateOrder[Create Order record]
    CreateOrder --> CreateItems[Create OrderItems]
    CreateItems --> ReduceStock[Reduce product stock]
    ReduceStock --> ClearCart[Clear cart items]
    ClearCart --> SetPayment{Payment method?}
    SetPayment -->|COD| Pending[payment_status = pending]
    SetPayment -->|Online| Completed[payment_status = completed]
    Pending --> Confirm[Order Confirmation Page]
    Completed --> Confirm
```

---

## 6. Admin Lite — Product Management

```mermaid
flowchart TD
    Login[Admin Login<br/>admin / admin] --> Panel[/panel/ Dashboard]

    Panel --> ProdList[/panel/products/]
    Panel --> AddBtn[Add Product]

    ProdList --> Actions{Action}
    Actions -->|View| StoreView[View on storefront]
    Actions -->|Edit| EditForm[Edit Product Form]
    Actions -->|Delete| DeleteConfirm[Confirm Delete]

    AddBtn --> AddForm[Product Form]
    AddForm --> Fields[Fill: name, description,<br/>price, MRP, stock, image, category]
    Fields --> Save[Save Product]
    EditForm --> Save

    Save --> DB[(Database)]
    DeleteConfirm -->|Confirm| RemoveDB[Delete from DB]
    RemoveDB --> ProdList
    DB --> ProdList
```

---

## 7. Admin Lite — Order Management

```mermaid
flowchart TD
    Orders[/panel/orders/] --> Filter{Filter by status?}
    Filter --> OrderList[Display orders table]
    OrderList --> ViewOrder[Click View]

    ViewOrder --> OrderDetail[Order Detail Page]
    OrderDetail --> ShowInfo[Customer info + items + total]
    ShowInfo --> UpdateForm[Update status form]

    UpdateForm --> StatusChange{Update}
    StatusChange --> OrderStatus[pending → processing → shipped → delivered]
    StatusChange --> PayStatus[pending → completed / failed]
    StatusChange --> Notes[Add admin notes]

    OrderStatus --> Save[Save Changes]
    PayStatus --> Save
    Notes --> Save
    Save --> OrderDetail
```

---

## 8. Data Setup Flow (setup_initial_data)

```mermaid
flowchart TD
    Run[python manage.py setup_initial_data] --> Step1[Create admin user]
    Step1 --> AdminCreds[username: admin<br/>password: admin<br/>is_staff: True<br/>is_superuser: True]

    AdminCreds --> Step2[Create categories]
    Step2 --> Cats[Kitchen, Drinkware,<br/>Lunch Boxes, Home Essentials]

    Cats --> Step3[Scan media/products/]
    Step3 --> Files{Image files found?}

    Files -->|Yes| MapData[Map filename to product metadata]
    MapData --> CreateProd[Create/Update Product records]
    CreateProd --> LinkImage[Link image path products/filename.jpeg]
    LinkImage --> Done[13 products loaded]

    Files -->|No| Warn[Warning: no images found]
    Warn --> Done
```

---

## 9. Request Routing Flow

```mermaid
flowchart LR
    Request[HTTP Request] --> Root[oceanix/urls.py]

    Root -->|/admin/| DjangoAdmin[Django Admin]
    Root -->|/*| StoreURLs[store/urls.py]

    StoreURLs --> Public[Public Views]
    StoreURLs --> Auth[Login Required]
    StoreURLs --> Staff[Staff Required]

    Public --> Home[home]
    Public --> Detail[product_detail]
    Public --> Login[login / register]

    Auth --> Cart[cart_view]
    Auth --> Checkout[checkout]
    Auth --> Orders[order_history]

    Staff --> Panel[admin_dashboard]
    Staff --> ProdCRUD[add/edit/delete product]
    Staff --> OrderAdmin[admin_order_list]
```

---

## 10. Order Lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending : Order placed
    pending --> processing : Admin updates status
    processing --> shipped : Order dispatched
    shipped --> delivered : Customer receives
    pending --> cancelled : Order cancelled
    processing --> cancelled : Order cancelled

    note right of pending
        COD: payment_status = pending
        Online: payment_status = completed
    end note

    delivered --> [*]
    cancelled --> [*]
```
