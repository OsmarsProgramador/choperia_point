# produto/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='replace_comma')
def replace_comma(value):
    """
    Substitui vírgulas por pontos em valores numéricos.
    """
    try:
        return str(value).replace(',', '.')
    except (ValueError, TypeError):
        return value

