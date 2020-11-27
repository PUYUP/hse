from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import utils
from django.views import View
from django.shortcuts import render
from django.conf import settings

from utils.generals import get_model
from utils.pagination import Pagination

User = get_model('person', 'User')


class LearnerView(View):
    template_name = 'console/learner.html'
    context = {}

    def get(self, request):
        queryset = User.objects.prefetch_related('account', 'profile') \
            .select_related('account', 'profile') \
            .filter(is_staff=False)
        
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(queryset, settings.PAGINATION_PER_PAGE)

        try:
            queryset_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            queryset_pagination = paginator.page(1)
        except EmptyPage:
            queryset_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, queryset, queryset_pagination, page_num, paginator)

        self.context['queryset'] = queryset
        self.context['queryset_pagination'] = queryset_pagination
        self.context['pagination'] = pagination
        return render(self.request, self.template_name, self.context)
