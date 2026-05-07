from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product


def make_product(category, name="Морковь", slug="carrot", in_stock=True):
    return Product.objects.create(
        category=category,
        name=name,
        slug=slug,
        description="Описание",
        price=100.00,
        weight="1 кг",
        calories="35 ккал",
        protein="1г",
        fat="0г",
        carbs="7г",
        in_stock=in_stock,
    )


class ProductListViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Овощи", slug="vegetables")
        self.product = make_product(self.category)
        self.url = reverse("products:product_list")

    def test_status_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_products(self):
        response = self.client.get(self.url)
        self.assertIn("products", response.context)

    def test_context_contains_categories(self):
        response = self.client.get(self.url)
        self.assertIn("categories", response.context)

    def test_out_of_stock_excluded(self):
        make_product(self.category, name="Лук", slug="onion", in_stock=False)
        response = self.client.get(self.url)
        names = [p.name for p in response.context["products"]]
        self.assertIn("Морковь", names)
        self.assertNotIn("Лук", names)

    def test_category_filter(self):
        other_cat = Category.objects.create(name="Фрукты", slug="fruits")
        make_product(other_cat, name="Яблоко", slug="apple")
        response = self.client.get(self.url, {"category": "fruits"})
        names = [p.name for p in response.context["products"]]
        self.assertIn("Яблоко", names)
        self.assertNotIn("Морковь", names)


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Овощи", slug="vegetables")
        self.product = make_product(self.category)

    def test_status_200(self):
        url = reverse("products:product_detail", args=[self.product.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_product(self):
        url = reverse("products:product_detail", args=[self.product.slug])
        response = self.client.get(url)
        self.assertEqual(response.context["product"], self.product)

    def test_404_for_unknown_slug(self):
        response = self.client.get("/nonexistent-product/")
        self.assertEqual(response.status_code, 404)
