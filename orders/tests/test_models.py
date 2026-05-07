from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Category, Product
from orders.models import Order, OrderItem


def make_product(category):
    return Product.objects.create(
        category=category,
        name="Морковь",
        slug="carrot",
        description="Описание",
        price=150.00,
        weight="1 кг",
        calories="35 ккал",
        protein="1г",
        fat="0г",
        carbs="7г",
    )


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        category = Category.objects.create(name="Овощи", slug="vegetables")
        self.product = make_product(category)
        self.order = Order.objects.create(
            user=self.user,
            phone="+71234567890",
            address="Тестовый адрес",
            status="new",
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_order=150.00,
        )

    def test_order_str(self):
        self.assertIn("testuser", str(self.order))

    def test_order_status_default(self):
        self.assertEqual(self.order.status, "new")

    def test_order_total_price(self):
        self.assertEqual(self.order.total_price(), 300.00)

    def test_order_item_total_price(self):
        self.assertEqual(self.item.total_price(), 300.00)

    def test_order_item_str(self):
        self.assertIn("Морковь", str(self.item))
