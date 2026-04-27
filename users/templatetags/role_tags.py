from django import template


register = template.Library()


@register.filter
def has_role(user, role_name: str) -> bool:
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name=role_name).exists())

