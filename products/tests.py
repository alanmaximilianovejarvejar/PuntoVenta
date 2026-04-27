from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from products.models import Product


class ProductModelTests(TestCase):
    def test_sale_price_cannot_be_lower_than_cost(self):
        product = Product(
            name="Producto",
            barcode="ABC",
            sale_price=Decimal("5.00"),
            cost=Decimal("6.00"),
            stock_current=Decimal("1.00"),
            min_stock=Decimal("1.00"),
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

