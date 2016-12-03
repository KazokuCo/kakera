# Some of these are shamelessly stolen from the wagtail demo project:
# https://github.com/torchbox/wagtaildemo/blob/master/demo/templatetags/demo_tags.py
from django import template

register = template.Library()

def has_menu_children(page):
    return page.get_children().live().in_menu().exists()

@register.inclusion_tag('kakera_core/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menu_items = parent.get_children().live().in_menu()
    for item in menu_items:
        item.show_dropdown = has_menu_children(item)
        item.active = calling_page.url.startswith(item.url) if calling_page else False
    return {
        'calling_page': calling_page,
        'menu_items': menu_items,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }

@register.inclusion_tag('kakera_core/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent, calling_page=None):
    menu_items = parent.get_children().live().in_menu()
    for item in menu_items:
        item.show_dropdown = has_menu_children(item)
        item.active = calling_page.url.startswith(item.url) if calling_page else False
    return {
        'parent': parent,
        'menu_items': menu_items,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }

@register.simple_tag
def get_site_theme(site):
    return site.themes.filter(active=True).first()
