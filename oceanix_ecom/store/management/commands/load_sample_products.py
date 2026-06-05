"""Management command to load sample products and categories."""
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = 'Load sample categories and products into the database'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Kitchen', 'slug': 'kitchen', 'icon': 'fa-utensils'},
            {'name': 'Drinkware', 'slug': 'drinkware', 'icon': 'fa-glass-water'},
            {'name': 'Lunch Boxes', 'slug': 'lunch-boxes', 'icon': 'fa-box'},
            {'name': 'Home Essentials', 'slug': 'home-essentials', 'icon': 'fa-home'},
        ]

        cat_map = {}
        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'icon': cat_data['icon']}
            )
            cat_map[cat_data['slug']] = cat
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: Category {cat.name}')

        products = [
            {
                'name': 'Professional Stainless Steel Coconut Opener Tool',
                'short_description': 'Easy tender coconut opener with ergonomic handle',
                'category': 'kitchen',
                'highlights': 'Rust-resistant stainless steel\nOpens coconuts in seconds\nErgonomic non-slip handle\nIdeal for home and juice shops',
                'description': '''Professional Stainless Steel Coconut Opener Tool for Tender Coconut | Easy Coconut Water Opening Tool | Heavy Duty Coconut Puncher | Ergonomic Handle

Open Tender Coconuts in Seconds
This premium coconut opener is specially designed to make opening green tender coconuts quick, safe, and effortless. Its sharp stainless steel piercing tip easily creates an opening without the need for heavy knives or dangerous tools.

Premium Stainless Steel Construction
Made from high-quality rust-resistant stainless steel, this coconut opener offers long-lasting durability, strength, and excellent performance for daily use at home, restaurants, juice shops, and outdoor events.''',
                'price': 299.99,
                'mrp': 499.99,
                'rating': 4.3,
                'review_count': 128,
                'stock': 50,
            },
            {
                'name': 'Leakproof Water Bottle with Silicone Sleeve & Carry Handle',
                'short_description': 'BPA-free reusable bottle with protective sleeve',
                'category': 'drinkware',
                'highlights': 'BPA-free glass body\nLeakproof flip-lock lid\nSilicone protective sleeve\nErgonomic carry handle',
                'description': '''1 Pcs Leakproof Water Bottle with Silicone Sleeve & Carry Handle | BPA Free Reusable Drinking Bottle | Portable Sports, Gym, Office, School & Travel Water Bottle

Stay hydrated throughout the day with this premium Water Bottle featuring a protective silicone sleeve and convenient carry handle. Designed for everyday use, this stylish and durable bottle is perfect for carrying water, juice, detox drinks, and other beverages.''',
                'price': 599.99,
                'mrp': 899.99,
                'rating': 4.5,
                'review_count': 256,
                'stock': 75,
            },
            {
                'name': '6 Pcs Unbreakable Fiber Plastic Water Glass Set',
                'short_description': 'Transparent unbreakable tumblers for daily use',
                'category': 'drinkware',
                'highlights': 'Set of 6 glasses\nUnbreakable fiber plastic\nDishwasher safe\nElegant transparent look',
                'description': '''6 Pcs Unbreakable Fiber Plastic Water Glass Set | Transparent Drinking Tumblers for Home, Kitchen & Daily Use

Upgrade your drinkware collection with this premium 6-piece transparent fiber plastic glass set, designed for everyday use.''',
                'price': 449.99,
                'mrp': 699.99,
                'rating': 4.1,
                'review_count': 89,
                'stock': 60,
            },
            {
                'name': 'Ice Infuser Water Bottle with Straw & Handle',
                'short_description': 'Fruit infuser sports bottle with straw',
                'category': 'drinkware',
                'highlights': 'Built-in infuser tube\nBPA-free material\nLeakproof lid with straw\nErgonomic handle',
                'description': '''Ice Infuser Water Bottle with Straw & Handle | BPA-Free Reusable Water Bottle | Fruit Infuser Sports Bottle | Leakproof Travel Water Bottle for Gym, Office, School & Outdoor Use | 1 Piece''',
                'price': 549.99,
                'mrp': 799.99,
                'rating': 4.4,
                'review_count': 167,
                'stock': 80,
            },
            {
                'name': '3 Compartment Stainless Steel Lunch Box with Fiber Outer Body',
                'short_description': 'Leakproof bento lunch box for office & school',
                'category': 'lunch-boxes',
                'highlights': '3 separate compartments\nFood-grade stainless steel\nLeakproof airtight lid\nLightweight fiber body',
                'description': '''3 Compartment Stainless Steel Lunch Box with Fiber Outer Body | Leakproof Bento Lunch Container for Office, School & Travel''',
                'price': 699.99,
                'mrp': 999.99,
                'rating': 4.6,
                'review_count': 312,
                'stock': 45,
            },
            {
                'name': 'Stainless Steel Lunch Box with Soup Container & Spoon',
                'short_description': 'Complete meal solution with soup container',
                'category': 'lunch-boxes',
                'highlights': '3 compartments + soup container\nIncludes spoon\nBPA-free outer body\nSecure locking clips',
                'description': '''Stainless Steel and Fiber 3-Compartment Lunch Box with Soup Container & Spoon | Leakproof Bento Lunch Box for Kids & Adults | BPA-Free Food Storage Container''',
                'price': 799.99,
                'mrp': 1199.99,
                'rating': 4.7,
                'review_count': 445,
                'stock': 55,
            },
        ]

        for product_data in products:
            category = cat_map.get(product_data.pop('category'))
            name = product_data['name']
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={**product_data, 'category': category, 'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Exists: {product.name}'))

        self.stdout.write(self.style.SUCCESS('\nSample data loaded successfully!'))
