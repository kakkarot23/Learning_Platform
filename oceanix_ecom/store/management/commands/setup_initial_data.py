"""Create admin user and load products from media/products folder."""
import os
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from store.models import Category, Product


MEDIA_PRODUCTS = [
    {
        'filename': '24141241.jpeg',
        'name': '3-Compartment Lunch Box with Soup Container & Spoon',
        'short_description': 'Leakproof bento lunch box with soup bowl and spoon',
        'category': 'lunch-boxes',
        'price': Decimal('799.99'),
        'mrp': Decimal('1199.99'),
        'rating': Decimal('4.7'),
        'review_count': 312,
        'stock': 45,
        'highlights': '3 separate food compartments\nIncludes soup container and spoon\nFood-grade stainless steel inner tray\nLeakproof snap-lock lid',
        'description': (
            'Keep your meals fresh and organized with this premium 3-compartment lunch box. '
            'Features a removable stainless steel tray, leakproof lid, and a separate soup '
            'container with matching spoon. Perfect for office, school, and travel.'
        ),
    },
    {
        'filename': 'fefqfqw.jpeg',
        'name': 'Wall-Mounted Chrome Spice Rack with 3 Glass Jars',
        'short_description': 'Modern wall spice organizer with textured glass jars',
        'category': 'kitchen',
        'price': Decimal('549.99'),
        'mrp': Decimal('899.99'),
        'rating': Decimal('4.4'),
        'review_count': 178,
        'stock': 60,
        'highlights': 'Chrome-plated wire frame\n3 textured glass jars included\nEasy wall mounting\nSpace-saving kitchen organizer',
        'description': (
            'Organize your spices with this sleek wall-mounted chrome spice rack. '
            'Comes with three elegant hammered-texture glass jars with brushed metal lids. '
            'Saves counter space and adds a modern touch to your kitchen.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 15.55.55.jpeg',
        'name': '3 Compartment Stainless Steel Lunch Box Set',
        'short_description': 'Multi-color bento boxes with steel inner tray',
        'category': 'lunch-boxes',
        'price': Decimal('699.99'),
        'mrp': Decimal('999.99'),
        'rating': Decimal('4.6'),
        'review_count': 245,
        'stock': 50,
        'highlights': 'Available in Grey, Pink & Blue\nStainless steel 3-compartment tray\n4 secure snap-lock clips\nSteam-vent transparent lid',
        'description': (
            'Premium 3-compartment lunch boxes with durable plastic outer body and '
            'food-grade stainless steel inner tray. Keeps food separate and fresh. '
            'Ideal for office lunches, school meals, and meal prep.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 15.55.56.jpeg',
        'name': 'Ice Infuser Water Bottle with Straw & Handle',
        'short_description': 'BPA-free bottle with built-in ice core and straw',
        'category': 'drinkware',
        'price': Decimal('449.99'),
        'mrp': Decimal('699.99'),
        'rating': Decimal('4.3'),
        'review_count': 156,
        'stock': 80,
        'highlights': 'Built-in ice infuser core\nBPA-free reusable material\nLeakproof lid with straw\nErgonomic carry handle',
        'description': (
            'Stay cool and hydrated with this Ice Bottle featuring a central infuser core '
            'for ice cubes and fruits. Includes a convenient straw, leakproof lid, and '
            'side handle. Perfect for gym, office, and outdoor activities.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 15.55.57.jpeg',
        'name': '12 Pcs Classic Faceted Glass Tumbler Set',
        'short_description': 'Elegant faceted glass tumblers for daily use',
        'category': 'drinkware',
        'price': Decimal('399.99'),
        'mrp': Decimal('649.99'),
        'rating': Decimal('4.5'),
        'review_count': 203,
        'stock': 70,
        'highlights': 'Set of 12 glasses\nClassic faceted design\nDurable clear glass\nPerfect for juice, water & cocktails',
        'description': (
            'Upgrade your drinkware with this set of 12 classic faceted glass tumblers. '
            'Elegant vertical panel design with a heavy octagonal base. '
            'Ideal for water, juice, iced tea, and everyday dining.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.02.41.jpeg',
        'name': 'Leakproof Water Bottle with Silicone Sleeve & Handle',
        'short_description': 'Glass bottle with protective sleeve in 3 colors',
        'category': 'drinkware',
        'price': Decimal('599.99'),
        'mrp': Decimal('899.99'),
        'rating': Decimal('4.6'),
        'review_count': 289,
        'stock': 75,
        'highlights': 'BPA-free glass inner body\nProtective silicone sleeve\nLeakproof flip-lock lid\nBuilt-in carry handle',
        'description': (
            'Premium leakproof water bottle with clear glass body and colorful protective '
            'silicone sleeve. Features a secure flip-lock lid and ergonomic carry handle. '
            'Available in Blue, White, and Pink.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.03.18.jpeg',
        'name': 'Professional Stainless Steel Coconut Opener Tool',
        'short_description': 'Easy tender coconut opener with T-handle grip',
        'category': 'kitchen',
        'price': Decimal('299.99'),
        'mrp': Decimal('499.99'),
        'rating': Decimal('4.4'),
        'review_count': 134,
        'stock': 90,
        'highlights': 'Rust-resistant stainless steel\nOpens coconuts in seconds\nErgonomic T-handle design\nSafe and easy to use',
        'description': (
            'Open tender coconuts quickly and safely with this professional stainless steel '
            'coconut opener. Sharp piercing tip with ergonomic T-handle for comfortable grip. '
            'Perfect for home, restaurants, and juice shops.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.05.47.jpeg',
        'name': 'Wall-Mounted Bathroom Storage Cabinet',
        'short_description': 'Modern bathroom organizer with tinted doors',
        'category': 'home-essentials',
        'price': Decimal('1299.99'),
        'mrp': Decimal('1999.99'),
        'rating': Decimal('4.5'),
        'review_count': 87,
        'stock': 30,
        'highlights': '3-tier internal shelving\nSmoke-tinted ribbed doors\nBottom hooks for towels\nSpace-saving wall mount',
        'description': (
            'Maximize bathroom storage with this sleek wall-mounted cabinet. Features '
            'smoke-tinted ribbed doors, three internal shelves, and bottom hooks for '
            'towels and accessories. Modern design for any bathroom.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.40.54dwedwe.jpeg',
        'name': 'Clear Jewelry Organizer Box with Compartments',
        'short_description': 'Transparent storage box with removable mini cases',
        'category': 'home-essentials',
        'price': Decimal('349.99'),
        'mrp': Decimal('549.99'),
        'rating': Decimal('4.2'),
        'review_count': 96,
        'stock': 55,
        'highlights': 'Transparent ribbed plastic\nRemovable individual compartments\nHinged flip-top lid\nPerfect for jewelry & accessories',
        'description': (
            'Keep jewelry organized with this clear ribbed storage box. Features a hinged '
            'main lid and multiple removable square compartments for bracelets, earrings, '
            'and small accessories.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.40.54wdwqd.jpeg',
        'name': 'Gas Cylinder Trolley with Wheels & Pull Handle',
        'short_description': 'Heavy-duty blue trolley for easy cylinder movement',
        'category': 'home-essentials',
        'price': Decimal('499.99'),
        'mrp': Decimal('799.99'),
        'rating': Decimal('4.3'),
        'review_count': 112,
        'stock': 40,
        'highlights': '4 smooth-rolling caster wheels\nConvenient pull string handle\nDurable reinforced plastic\nEasy gas cylinder mobility',
        'description': (
            'Move gas cylinders effortlessly with this durable blue plastic trolley. '
            'Features four caster wheels and a pull handle with string. '
            'Reinforced circular design for stability and long-lasting use.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.40.55dwsd.jpeg',
        'name': 'Bear Family Kids Lunch Box Set',
        'short_description': 'Cute 3-compartment lunch box for kids',
        'category': 'lunch-boxes',
        'price': Decimal('649.99'),
        'mrp': Decimal('949.99'),
        'rating': Decimal('4.8'),
        'review_count': 367,
        'stock': 65,
        'highlights': 'Bear Family cartoon design\n3 color options: Green, Pink, Blue\nStainless steel inner tray\nLeakproof snap-lock lid',
        'description': (
            'Make lunchtime fun with the Bear Family kids lunch box set. Features a '
            '3-compartment stainless steel tray, cute bear illustrations, and secure '
            'snap-lock lids. Available in Green, Pink, and Teal Blue.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.40.56.jpeg',
        'name': 'Hungry Lunch Box & Water Bottle Combo Set',
        'short_description': 'Matching lunch box and bottle set for kids',
        'category': 'lunch-boxes',
        'price': Decimal('749.99'),
        'mrp': Decimal('1099.99'),
        'rating': Decimal('4.7'),
        'review_count': 298,
        'stock': 48,
        'highlights': '3-compartment lunch box\nMatching water bottle included\nWrist strap on bottle\nTeal, Purple & Coral colors',
        'description': (
            'Complete lunch set with matching Hungry branded lunch box and water bottle. '
            '3-compartment tray with fun food illustrations. Leakproof snap-lock lids '
            'and fabric wrist strap. Perfect for school and picnics.'
        ),
    },
    {
        'filename': 'WhatsApp Image 2026-06-05 at 16.40.57.jpeg',
        'name': 'Motivational Time Marker Water Bottle Set',
        'short_description': 'Hydration tracker bottles with time markers',
        'category': 'drinkware',
        'price': Decimal('549.99'),
        'mrp': Decimal('849.99'),
        'rating': Decimal('4.5'),
        'review_count': 221,
        'stock': 85,
        'highlights': 'Hourly time markers on bottle\nMotivational hydration quotes\n3 sizes: Slim, Standard & Jug\nBPA-free smoked grey plastic',
        'description': (
            'Track your daily water intake with these motivational time marker bottles. '
            'Features hourly reminders and encouraging quotes in English and Spanish. '
            'Available in three sizes with leak-proof lids and carry straps.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Create admin user (admin/admin) and load products from media/products'

    def handle(self, *args, **options):
        self._create_admin_user()
        self._ensure_categories()
        self._load_media_products()

    def _create_admin_user(self):
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@oceanix.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        user.set_password('admin')
        user.is_staff = True
        user.is_superuser = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin)'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated admin user password (username: admin, password: admin)'))

    def _ensure_categories(self):
        categories = [
            {'name': 'Kitchen', 'slug': 'kitchen', 'icon': 'fa-utensils'},
            {'name': 'Drinkware', 'slug': 'drinkware', 'icon': 'fa-glass-water'},
            {'name': 'Lunch Boxes', 'slug': 'lunch-boxes', 'icon': 'fa-box'},
            {'name': 'Home Essentials', 'slug': 'home-essentials', 'icon': 'fa-home'},
        ]
        for cat_data in categories:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'icon': cat_data['icon']}
            )

    def _load_media_products(self):
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if not os.path.isdir(products_dir):
            self.stdout.write(self.style.ERROR(f'Media folder not found: {products_dir}'))
            return

        loaded = 0
        for item in MEDIA_PRODUCTS:
            filepath = os.path.join(products_dir, item['filename'])
            if not os.path.isfile(filepath):
                self.stdout.write(self.style.WARNING(f'  Skipped (file missing): {item["filename"]}'))
                continue

            category = Category.objects.filter(slug=item['category']).first()
            image_path = f'products/{item["filename"]}'

            product, created = Product.objects.update_or_create(
                name=item['name'],
                defaults={
                    'short_description': item['short_description'],
                    'description': item['description'],
                    'highlights': item['highlights'],
                    'price': item['price'],
                    'mrp': item['mrp'],
                    'rating': item['rating'],
                    'review_count': item['review_count'],
                    'stock': item['stock'],
                    'category': category,
                    'is_active': True,
                    'image': image_path,
                }
            )

            loaded += 1
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'  {status}: {product.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nLoaded {loaded} products from media/products/'))
