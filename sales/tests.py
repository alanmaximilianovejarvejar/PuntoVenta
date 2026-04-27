from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from products.models import Category, Product
from sales.models import Sale
from sales.services.sale_service import SaleService


class SaleServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cashier", password="testpass")
        self.category = Category.objects.create(name="Abarrotes")
        self.product = Product.objects.create(
            category=self.category,
            name="Arroz 1 kg",
            barcode="123456789",
            sale_price=Decimal("10.00"),
            cost=Decimal("6.00"),
            stock_current=Decimal("5.00"),
            min_stock=Decimal("1.00"),
            tax_rate=Decimal("0.1600"),
        )

    def test_create_cash_sale_discounts_stock_and_calculates_change(self):
        sale = SaleService.create_sale(
            cashier=self.user,
            items=[{"product_id": self.product.pk, "quantity": "2"}],
            payment_method=Sale.PaymentMethod.CASH,
            amount_received=Decimal("30.00"),
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_current, Decimal("3.00"))
        self.assertEqual(sale.subtotal, Decimal("20.00"))
        self.assertEqual(sale.tax_total, Decimal("3.20"))
        self.assertEqual(sale.total, Decimal("23.20"))
        self.assertEqual(sale.change_given, Decimal("6.80"))

    def test_void_sale_restores_stock(self):
        sale = SaleService.create_sale(
            cashier=self.user,
            items=[{"product_id": self.product.pk, "quantity": "1"}],
            payment_method=Sale.PaymentMethod.CARD,
            amount_received=Decimal("0"),
        )

        SaleService.void_sale(sale=sale, user=self.user, reason="Prueba")
        self.product.refresh_from_db()
        sale.refresh_from_db()

        self.assertEqual(self.product.stock_current, Decimal("5.00"))
        self.assertEqual(sale.status, Sale.Status.VOIDED)

