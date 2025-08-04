from django import template

register = template.Library()


@register.filter
def leading_zero(value):
    """Add leading zero to single-digit numbers"""
    return f"{int(value):02d}"
