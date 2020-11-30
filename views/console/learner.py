from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.db.models import Count, Q

from utils.generals import get_model
from utils.pagination import Pagination

User = get_model('person', 'User')


class LearnerView(View):
    template_name = 'console/learner.html'
    context = {}

    def get(self, request):
        queryset = User.objects.prefetch_related('account', 'profile') \
            .annotate(
                enroll_count=Count('enroll', distinct=True),
                simulation_count=Count('simulation', distinct=True),
                answer_count=Count('simulation__answer', distinct=True),
                answer_count_survey=Count(
                    'simulation__answer', 
                    distinct=True,
                    filter=Q(simulation__answer__is_true=True) & Q(simulation__answer__course_quiz__position='survey')
                )
            ) \
            .select_related('account', 'profile')
        
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


class LearnerDetailView(View):
    template_name = 'console/learner-detail.html'
    context = {}

    def get(self, request, uuid=None):
        try:
            queryset = User.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            queryset = None
        
        self.context['uuid'] = uuid
        self.context['queryset'] = queryset
        return render(request, self.template_name, self.context)
