from django import template

register = template.Library()


@register.filter
def get_dict_value(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')  # Return an empty string if key is missing
    return ''  # Return empty if dictionary is None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)  # Default to 0 if key is missing
