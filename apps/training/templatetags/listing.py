from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.http import urlencode
from django.contrib.admin.views.main import (
    ALL_VAR, ORDER_VAR, PAGE_VAR, SEARCH_VAR,
)

register = Library()

DOT = '.'

def get_query_string(cl, new_params=None, remove=None):
    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    p = dict(cl.request.GET.items())
    for r in remove:
        for k in list(p):
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if v is None:
            if k in p:
                del p[k]
        else:
            p[k] = v
    return '?%s' % urlencode(sorted(p.items()))


@register.simple_tag
def paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    link_class = mark_safe(' class="page-link end rounded-0"' if i == cl.paginator.num_pages - 1 else 'class="page-link rounded-0"')
    page_var = get_query_string(cl, {PAGE_VAR: i})

    if i == DOT:
        return format_html('<li class="page-item disabled"><span class="page-link rounded-0">...</span></li>')
    elif i == cl.page_num:
        return format_html(
            '<li class="page-item active"><a href="{}"{}>{}</a></li>',
            page_var,
            link_class,
            i + 1
        )
    else:
        return format_html(
            '<li class="page-item"><a href="{}"{}>{}</a></li>',
            page_var,
            link_class,
            i + 1,
        )


def pagination(cl):
    """
    Generate the series of links to the pages in a paginated list.
    """
    paginator, page_num = cl.paginator, cl.page_num

    pagination_required = (not cl.show_all or not cl.can_show_all) and cl.multi_page
    if not pagination_required:
        page_range = []
    else:
        ON_EACH_SIDE = 3
        ON_ENDS = 2

        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if paginator.num_pages <= 10:
            page_range = range(paginator.num_pages)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range += [
                    *range(0, ON_ENDS), DOT,
                    *range(page_num - ON_EACH_SIDE, page_num + 1),
                ]
            else:
                page_range.extend(range(0, page_num + 1))
            if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range += [
                    *range(page_num + 1, page_num + ON_EACH_SIDE + 1), DOT,
                    *range(paginator.num_pages - ON_ENDS, paginator.num_pages)
                ]
            else:
                page_range.extend(range(page_num + 1, paginator.num_pages))

    need_show_all_link = cl.can_show_all and not cl.show_all and cl.multi_page
    return {
        'cl': cl,
        'pagination_required': pagination_required,
        'show_all_url': need_show_all_link and get_query_string(cl, {ALL_VAR: ''}),
        'page_range': page_range,
        'ALL_VAR': ALL_VAR,
        '1': 1,
    }

register.inclusion_tag('pagination.html')(pagination)
