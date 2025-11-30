from django import template

register = template.Library()

@register.filter
def rupee_format(value):
    try:
        number = float(value)
        return f"₹{number:,.2f}"
    except (TypeError, ValueError):
        return value

