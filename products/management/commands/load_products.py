import json
from django.core.management.base import BaseCommand
from products.models import Category, Product

class Command(BaseCommand):
    help = 'Load products from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file with products data')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {json_file} not found'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON format in {json_file}'))
            return

        # Category mapping from English to Russian
        category_mapping = {
            'vegetables': 'Овощи',
            'meat': 'Мясо',
            'dairy': 'Молочные продукты',
            'fruits': 'Фрукты',
            'berries': 'Ягоды',
            'bakery': 'Выпечка',
            'preserves': 'Заготовки',
            'sweets': 'Сладости'
        }

        # Create categories
        categories = {}
        for category_slug, category_name in category_mapping.items():
            category, created = Category.objects.get_or_create(
                slug=category_slug,
                defaults={'name': category_name}
            )
            categories[category_slug] = category
            if created:
                self.stdout.write(f'Created category: {category_name}')
            else:
                self.stdout.write(f'Category already exists: {category_name}')

        # Create products
        products_created = 0
        products_updated = 0

        for product_data in products_data:
            category_slug = product_data['category']
            category = categories.get(category_slug)
            
            if not category:
                self.stdout.write(self.style.WARNING(
                    f'Skipping product "{product_data["name"]}" - unknown category "{category_slug}"'
                ))
                continue

            # Prepare product data
            product_fields = {
                'category': category,
                'name': product_data['name'],
                'description': product_data['description'],
                'price': product_data['price'],
                'weight': product_data['weight'],
                'calories': product_data['calories'],
                'protein': product_data['protein'],
                'fat': product_data['fat'],
                'carbs': product_data['carbs'],
                'in_stock': product_data['in_stock']
            }

            # Create or update product
            product, created = Product.objects.update_or_create(
                name=product_data['name'],
                defaults=product_fields
            )

            if created:
                products_created += 1
                self.stdout.write(f'Created product: {product.name}')
            else:
                products_updated += 1
                self.stdout.write(f'Updated product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded products: {products_created} created, {products_updated} updated'
            )
        )