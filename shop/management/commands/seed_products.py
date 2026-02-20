from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Napuni bazu testnim patikama (više brandova)'

    def handle(self, *args, **options):
        from shop.models import Product

        sample = [
            # Nike
            {
                'title': 'Air Max 90',
                'brand': 'Nike',
                'price': '129.99',
            },
            {
                'title': 'Air Force 1',
                'brand': 'Nike',
                'price': '99.99',
            },
            {
                'title': 'Air VaporMax',
                'brand': 'Nike',
                'price': '189.99',
            },
            {
                'title': 'React Infinity Run',
                'brand': 'Nike',
                'price': '159.99',
            },
            {
                'title': 'ZoomX Invincible',
                'brand': 'Nike',
                'price': '179.99',
            },
            {
                'title': 'Pegasus Trail',
                'brand': 'Nike',
                'price': '139.99',
            },
            {
                'title': 'Blazer Mid',
                'brand': 'Nike',
                'price': '89.99',
            },
            {
                'title': 'SB Dunk Low',
                'brand': 'Nike',
                'price': '110.00',
            },
            {
                'title': 'Air Zoom Pegasus',
                'brand': 'Nike',
                'price': '119.99',
            },
            {
                'title': 'Cortez',
                'brand': 'Nike',
                'price': '74.99',
            },
            # Adidas
            {
                'title': 'Ultraboost 1.0 DNA',
                'brand': 'Adidas',
                'price': '180.00',
            },
            {
                'title': 'NMD_R1',
                'brand': 'Adidas',
                'price': '140.00',
            },
            {
                'title': 'Superstar',
                'brand': 'Adidas',
                'price': '95.00',
            },
            {
                'title': 'Stan Smith',
                'brand': 'Adidas',
                'price': '100.00',
            },
            {
                'title': 'Forum Low',
                'brand': 'Adidas',
                'price': '110.00',
            },
            {
                'title': 'Gazelle',
                'brand': 'Adidas',
                'price': '100.00',
            },
            {
                'title': 'Campus 00s',
                'brand': 'Adidas',
                'price': '110.00',
            },
            {
                'title': 'Adizero Boston 12',
                'brand': 'Adidas',
                'price': '170.00',
            },
            {
                'title': 'Samba OG',
                'brand': 'Adidas',
                'price': '120.00',
            },
            {
                'title': 'Solar Glide 6',
                'brand': 'Adidas',
                'price': '135.00',
            },
            # New Balance
            {
                'title': '990v6',
                'brand': 'New Balance',
                'price': '200.00',
            },
            {
                'title': '550',
                'brand': 'New Balance',
                'price': '120.00',
            },
            {
                'title': '327',
                'brand': 'New Balance',
                'price': '110.00',
            },
            {
                'title': 'Fresh Foam 1080v13',
                'brand': 'New Balance',
                'price': '165.00',
            },
            {
                'title': 'FuelCell Rebel v3',
                'brand': 'New Balance',
                'price': '140.00',
            },
            {
                'title': 'Made in USA 998',
                'brand': 'New Balance',
                'price': '210.00',
            },
            {
                'title': 'XC-72',
                'brand': 'New Balance',
                'price': '120.00',
            },
            {
                'title': 'Fresh Foam X More v4',
                'brand': 'New Balance',
                'price': '150.00',
            },
            {
                'title': '574 Core',
                'brand': 'New Balance',
                'price': '85.00',
            },
            {
                'title': '860v13',
                'brand': 'New Balance',
                'price': '140.00',
            },
            # Vans
            {
                'title': 'Old Skool',
                'brand': 'Vans',
                'price': '80.00',
            },
            {
                'title': 'Sk8-Hi',
                'brand': 'Vans',
                'price': '85.00',
            },
            {
                'title': 'Authentic',
                'brand': 'Vans',
                'price': '65.00',
            },
            {
                'title': 'Era',
                'brand': 'Vans',
                'price': '60.00',
            },
            {
                'title': 'Slip-On',
                'brand': 'Vans',
                'price': '60.00',
            },
            {
                'title': 'UltraRange Exo',
                'brand': 'Vans',
                'price': '100.00',
            },
            {
                'title': 'Rowan 2',
                'brand': 'Vans',
                'price': '70.00',
            },
            {
                'title': 'AVE Pro',
                'brand': 'Vans',
                'price': '110.00',
            },
            {
                'title': 'Kyle Pro 2',
                'brand': 'Vans',
                'price': '95.00',
            },
            {
                'title': 'Half Cab',
                'brand': 'Vans',
                'price': '90.00',
            },
        ]

        def build_unsplash_image_url(brand: str, title: str) -> str:
            brand_slug = brand.lower().replace(' ', '-').replace("'", '')
            title_slug = title.lower().replace(' ', '-').replace("'", '')
            return f"https://source.unsplash.com/800x600/?{brand_slug},{title_slug},sneakers"

        created = 0
        for item in sample:
            p, created_flag = Product.objects.get_or_create(
                title=item['title'],
                defaults={
                    'brand': item['brand'],
                    'price': item['price'],
                    'image_url': item.get('image_url') or build_unsplash_image_url(item['brand'], item['title']),
                    'description': f"Primjer modela {item['title']} iz kolekcije {item['brand']}.",
                }
            )
            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} products (or already existed).'))
