from django import forms

from products.models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]
        labels = {
            "name": "Nombre",
            "description": "Descripcion",
            "is_active": "Activa",
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "sku",
            "barcode",
            "description",
            "image",
            "sale_price",
            "cost",
            "stock_current",
            "min_stock",
            "tax_rate",
            "is_active",
        ]
        labels = {
            "category": "Categoria",
            "name": "Nombre",
            "sku": "SKU",
            "barcode": "Codigo de barras",
            "description": "Descripcion",
            "image": "Imagen",
            "sale_price": "Precio de venta",
            "cost": "Costo",
            "stock_current": "Stock actual",
            "min_stock": "Stock minimo",
            "tax_rate": "Impuesto",
            "is_active": "Activo",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "sale_price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "stock_current": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "min_stock": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "tax_rate": forms.NumberInput(attrs={"step": "0.0001", "min": "0"}),
        }
