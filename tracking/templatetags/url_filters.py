from django import template

register = template.Library()

@register.filter
def remove_duplicate_page(url):
    parts = url.split('page=', 1)
    return parts[0]