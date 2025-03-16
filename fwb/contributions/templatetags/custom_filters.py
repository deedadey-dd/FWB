from django import template

register = template.Library()


@register.filter
def get_dict_value(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')  # Return an empty string if key is missing
    return ''  # Return empty if dictionary is None
