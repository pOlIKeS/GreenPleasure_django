from decimal import Decimal
from django.test import TestCase
from products.models import Category, Product


def make_product(category, name="Морковь", slug="carrot", in_stock=True, **kwargs):
    defaults = dict(
        description="Описание",
        price=Decimal("100.00"),
        weight="1 кг",
        calories="35 ккал",
        protein="1г",
        fat="0г",
        carbs="7г",
        in_stock=in_stock,
    )
    defaults.update(kwargs)
    return Product.objects.create(category=category, name=name, slug=slug, **defaults)


class CategoryModelTest(TestCase):
    def test_str(self):
        category = Category.objects.create(name="Овощи", slug="vegetables")
        self.assertEqual(str(category), "Овощи")

    def test_slug_auto_generated(self):
        category = Category.objects.create(name="Фрукты")
        self.assertTrue(category.slug)
        self.assertNotEqual(category.slug, "")


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Овощи", slug="vegetables")
        self.product = make_product(self.category)

    def test_str(self):
        self.assertEqual(str(self.product), "Морковь")

    def test_formatted_price(self):
        self.assertEqual(self.product.formatted_price(), "100.00 \u20bd")

    def test_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), "/carrot/")

    def test_in_stock_default_true(self):
        self.assertTrue(self.product.in_stock)

    def test_out_of_stock_product(self):
        product = make_product(self.category, name="Лук", slug="onion", in_stock=False)
        self.assertFalse(product.in_stock)

    def test_slug_auto_generated(self):
        product = make_product(self.category, name="Свёкла", slug="")
        self.assertTrue(product.slug)
