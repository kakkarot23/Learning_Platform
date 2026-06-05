"""Forms for store app."""
from django import forms
from django.contrib.auth.models import User
from .models import Order, Product, Category


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration."""
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match!')
        return cleaned_data


class UserLoginForm(forms.Form):
    """Form for user login."""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class OrderForm(forms.ModelForm):
    """Form for order information with payment method."""
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        initial='cod',
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'country', 'payment_method'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Street Address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }


class ProductForm(forms.ModelForm):
    """Form for product creation and editing."""
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'short_description', 'description', 'highlights',
            'price', 'mrp', 'discount_percent', 'rating', 'review_count',
            'stock', 'image', 'is_active'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name',
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Short one-line description for product cards',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full product description',
                'rows': 6,
            }),
            'highlights': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'One highlight per line',
                'rows': 4,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Selling Price (₹)',
                'step': '0.01',
                'min': '0',
            }),
            'mrp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'MRP (₹) - optional',
                'step': '0.01',
                'min': '0',
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Discount %',
                'min': '0',
                'max': '99',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rating (0-5)',
                'step': '0.1',
                'min': '0',
                'max': '5',
            }),
            'review_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of reviews',
                'min': '0',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stock Quantity',
                'min': '0',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('Price must be greater than 0!')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('Stock cannot be negative!')
        return stock


class OrderStatusForm(forms.ModelForm):
    """Form for updating order status in admin panel."""
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
