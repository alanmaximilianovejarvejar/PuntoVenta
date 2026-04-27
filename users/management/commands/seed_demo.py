from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from inventory.models import InventoryMovement
from products.models import Category, Product


class Command(BaseCommand):
    help = "Crea usuarios, roles, categorias y productos de prueba."

    def handle(self, *args, **options):
        User = get_user_model()

        admin_group, _ = Group.objects.get_or_create(name="admin")
        cashier_group, _ = Group.objects.get_or_create(name="cajero")
        admin_group.permissions.set(Permission.objects.all())

        cashier_permissions = Permission.objects.filter(
            content_type__app_label__in=["products", "sales"],
            codename__in=["view_product", "view_category", "add_sale", "view_sale", "add_saleitem", "view_saleitem"],
        )
        cashier_group.permissions.set(cashier_permissions)

        admin, _ = User.objects.update_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@cauloti.local"},
        )
        admin.set_password("admin12345")
        admin.save()
        admin.groups.add(admin_group)

        cashier, _ = User.objects.update_or_create(
            username="cajero",
            defaults={"is_staff": False, "is_superuser": False, "email": "cajero@cauloti.local"},
        )
        cashier.set_password("cajero12345")
        cashier.save()
        cashier.groups.add(cashier_group)

        categories = {
            "Abarrotes": "Productos de consumo diario",
            "Bebidas": "Bebidas frias y al tiempo",
            "Limpieza": "Articulos de limpieza",
            "Panaderia": "Pan y reposteria",
        }
        category_objs = {}
        for name, description in categories.items():
            category, _ = Category.objects.update_or_create(name=name, defaults={"description": description})
            category_objs[name] = category

        products = [
            ("Arroz 1 kg", "750100100001", "Abarrotes", "28.00", "19.50", "40", "8"),
            ("Frijol bayo 1 kg", "750100100002", "Abarrotes", "36.00", "25.00", "35", "8"),
            ("Aceite vegetal 900 ml", "750100100003", "Abarrotes", "48.50", "39.00", "24", "6"),
            ("Agua natural 1.5 L", "750100100004", "Bebidas", "18.00", "11.50", "60", "12"),
            ("Refresco cola 600 ml", "750100100005", "Bebidas", "19.00", "13.00", "48", "10"),
            ("Detergente polvo 1 kg", "750100100006", "Limpieza", "52.00", "38.00", "16", "5"),
            ("Cloro 1 L", "750100100007", "Limpieza", "21.50", "14.00", "22", "6"),
            ("Bolillo pieza", "750100100008", "Panaderia", "3.50", "1.80", "120", "25"),
            ("Pan dulce pieza", "750100100009", "Panaderia", "9.00", "4.50", "70", "15"),
            ("Cafe soluble 100 g", "750100100010", "Abarrotes", "74.00", "58.00", "12", "4"),
        ]

        for name, barcode, category_name, price, cost, stock, minimum in products:
            product, _ = Product.objects.update_or_create(
                barcode=barcode,
                defaults={
                    "name": name,
                    "sku": barcode[-6:],
                    "category": category_objs[category_name],
                    "sale_price": Decimal(price),
                    "cost": Decimal(cost),
                    "stock_current": Decimal(stock),
                    "min_stock": Decimal(minimum),
                    "tax_rate": Decimal("0.1600"),
                    "is_active": True,
                },
            )
            InventoryMovement.objects.get_or_create(
                product=product,
                movement_type=InventoryMovement.Type.IMPORT,
                reason="Seed inicial",
                defaults={
                    "quantity_delta": Decimal("0"),
                    "stock_after": product.stock_current,
                    "created_by": admin,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed completado. Usuarios: admin/admin12345, cajero/cajero12345"))

