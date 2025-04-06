from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def get_dict_value(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')  # Return an empty string if key is missing
    return ''  # Return empty if dictionary is None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)  # Default to 0 if key is missing


@register.filter(name='div')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter(name='mul')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0
