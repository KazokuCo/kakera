# Some of these are shamelessly stolen from the wagtail demo project:
# https://github.com/torchbox/wagtaildemo/blob/master/demo/templatetags/demo_tags.py
from django import template

register = template.Library()

def has_menu_children(page):
    return page.get_children().live().in_menu().exists()

@register.inclusion_tag('kakera_core/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menu_items = parent.get_children().live().in_menu()
    for menu_item in menu_items:
        menu_item.show_dropdown = has_menu_children(menu_item)
        menu_item.active = (calling_page.url.startswith(menu_item.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menu_items': menu_items,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }

@register.inclusion_tag('kakera_core/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent):
    menu_items_children = parent.get_children()
    menu_items_children = menu_items_children.live().in_menu()
    return {
        'parent': parent,
        'menu_items_children': menu_items_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }
