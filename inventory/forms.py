from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from products.models import Product


class InventoryAdjustmentForm(forms.Form):
    product = forms.ModelChoiceField(label="Producto", queryset=Product.objects.filter(is_active=True).order_by("name"))
    adjustment_type = forms.ChoiceField(
        label="Tipo de ajuste",
        choices=(("delta", "Sumar/restar"), ("set", "Definir existencia")),
        initial="delta",
    )
    quantity = forms.DecimalField(label="Cantidad", max_digits=12, decimal_places=2)
    reason = forms.CharField(label="Motivo", max_length=240)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity == Decimal("0"):
            raise ValidationError("La cantidad no puede ser cero.")
        return quantity
