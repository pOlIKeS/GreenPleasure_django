from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product


def make_product(category):
    return Product.objects.create(
        category=category,
        name="Морковь",
        slug="carrot",
        description="Описание",
        price=100.00,
        weight="1 кг",
        calories="35 ккал",
        protein="1г",
        fat="0г",
        carbs="7г",
    )


class CartTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Овощи", slug="vegetables")
        self.product = make_product(category)

    def test_cart_detail_empty(self):
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("cart_items", response.context)
        self.assertIn("total_price", response.context)
        self.assertEqual(len(response.context["cart_items"]), 0)
        self.assertEqual(response.context["total_price"], 0)

    def test_cart_add_creates_session_entry(self):
        self.client.get(reverse("orders:cart_add", args=[self.product.id]))
        cart = self.client.session.get("cart", {})
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)]["quantity"], 1)

    def test_cart_add_increments_quantity(self):
        url = reverse("orders:cart_add", args=[self.product.id])
        self.client.get(url)
        self.client.get(url)
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[str(self.product.id)]["quantity"], 2)

    def test_cart_remove_decrements_quantity(self):
        self.client.get(reverse("orders:cart_add", args=[self.product.id]))
        self.client.get(reverse("orders:cart_add", args=[self.product.id]))
        self.client.get(reverse("orders:cart_remove", args=[self.product.id]))
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[str(self.product.id)]["quantity"], 1)

    def test_cart_remove_deletes_when_quantity_one(self):
        self.client.get(reverse("orders:cart_add", args=[self.product.id]))
        self.client.get(reverse("orders:cart_remove", args=[self.product.id]))
        cart = self.client.session.get("cart", {})
        self.assertNotIn(str(self.product.id), cart)

    def test_cart_detail_shows_added_product(self):
        self.client.get(reverse("orders:cart_add", args=[self.product.id]))
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(len(response.context["cart_items"]), 1)
        self.assertEqual(response.context["cart_items"][0]["product"], self.product)
        self.assertEqual(response.context["total_price"], 100.0)
