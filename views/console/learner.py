from django.db.models.expressions import OuterRef, Subquery
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.db.models import Count, Q, F

from utils.generals import get_model
from utils.pagination import Pagination

User = get_model('person', 'User')
Simulation = get_model('training', 'Simulation')
Quiz = get_model('training', 'Quiz')


class LearnerView(View):
    template_name = 'console/learner.html'
    context = {}

    def get(self, request):
        quiz = Quiz.objects \
            .filter(simulation_quiz__simulation__uuid=OuterRef('uuid')) \
            .annotate(
                true_answer_survey=Count(
                    'simulation_quiz__answer',
                    distinct=True,
                    filter=Q(simulation_quiz__answer__is_true=True, simulation_quiz__answer__course_quiz__position='survey')
                ),
                true_answer_evaluate=Count(
                    'simulation_quiz__answer',
                    distinct=True,
                    filter=Q(simulation_quiz__answer__is_true=True, simulation_quiz__answer__course_quiz__position='evaluate')
                ),
                total_survey_question=Count('quiz_question', distinct=True),
                total_evaluate_question=Count('quiz_question', distinct=True)
            )

        simulation = Simulation.objects \
            .annotate(
                quiz_survey_true_answer=Subquery(quiz.filter(course_quiz__position='survey').values('true_answer_survey')[:1]),
                quiz_evaluate_true_answer=Subquery(quiz.filter(course_quiz__position='evaluate').values('true_answer_evaluate')[:1]),
                total_survey_question=Subquery(quiz.filter(course_quiz__position='survey').values('total_survey_question')[:1]),
                total_evaluate_question=Subquery(quiz.filter(course_quiz__position='evaluate').values('total_evaluate_question')[:1])
            ) \
            .filter(learner__uuid=OuterRef('uuid')) \
            .order_by('-quiz_survey_true_answer', '-quiz_evaluate_true_answer')

        queryset = User.objects.prefetch_related('account', 'profile') \
            .annotate(
                simulation_count=Count('simulation', distinct=True),
                quiz_survey_true_answer=Subquery(simulation.values('quiz_survey_true_answer')[:1]),
                quiz_evaluate_true_answer=Subquery(simulation.values('quiz_evaluate_true_answer')[:1]),
                total_survey_question=Subquery(simulation.values('total_survey_question')[:1]),
                total_evaluate_question=Subquery(simulation.values('total_evaluate_question')[:1])
            ) \
            .select_related('account', 'profile') \
            .order_by('-quiz_evaluate_true_answer', '-quiz_survey_true_answer')
        
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
        self.context['per_page'] = settings.PAGINATION_PER_PAGE
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
