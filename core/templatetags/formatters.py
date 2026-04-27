from decimal import Decimal

from django import template


register = template.Library()


@register.filter
def money(value):
    try:
        amount = Decimal(value or 0)
    except Exception:
        amount = Decimal("0")
    return f"${amount:,.2f}"


@register.filter
def qty(value):
    try:
        amount = Decimal(value or 0)
    except Exception:
        return value
    if amount == amount.to_integral_value():
        return f"{int(amount)}"
    return f"{amount.normalize()}"


@register.filter
def percent(value):
    try:
        amount = Decimal(value or 0) * 100
    except Exception:
        amount = Decimal("0")
    return f"{amount:.2f}%"

