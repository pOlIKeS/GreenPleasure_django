from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Category, Product
from orders.models import Order


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


class CheckoutViewTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Овощи", slug="vegetables")
        self.product = make_product(category)
        self.user = User.objects.create_user(username="buyer", password="pass123")

    def test_checkout_requires_login(self):
        url = reverse("orders:checkout")
        response = self.client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_checkout_empty_cart_redirects(self):
        self.client.login(username="buyer", password="pass123")
        response = self.client.get(reverse("orders:checkout"))
        self.assertRedirects(response, reverse("products:product_list"))

    def test_checkout_with_cart_returns_200(self):
        self.client.login(username="buyer", password="pass123")
        self.client.get(reverse("orders:cart_add", args=[self.product.id]))
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 200)


class OrderListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass123")

    def test_requires_login(self):
        url = reverse("orders:order_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_sees_only_own_orders(self):
        other_user = User.objects.create_user(username="other", password="pass123")
        category = Category.objects.create(name="Овощи", slug="vegetables")
        make_product(category)

        own_order = Order.objects.create(user=self.user, phone="111", address="Адрес")
        other_order = Order.objects.create(user=other_user, phone="222", address="Другой")

        self.client.login(username="buyer", password="pass123")
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(own_order, response.context["orders"])
        self.assertNotIn(other_order, response.context["orders"])
