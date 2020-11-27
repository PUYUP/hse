from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.generals import get_model
from utils.pagination import Pagination
from .forms import ChapterForm, CourseForm

Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourseQuiz')
Chapter = get_model('training', 'Chapter')


@method_decorator(login_required, name='dispatch')
class CourseView(View):
    template_name = 'console/course.html'
    context = {}

    def get_objects(self):
        queryset = Course.objects.prefetch_related('category') \
            .select_related('category') \
            .all()

        return queryset

    def get(self, request):
        queryset = self.get_objects()

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


@method_decorator(login_required, name='dispatch')
class CourseDetailView(View):
    template_name = 'console/course-detail.html'
    context = {}

    def get(self, request, uuid=None):
        try:
            queryset = Course.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            queryset = None
        
        self.context['queryset'] = queryset
        self.context['chapter'] = queryset.chapter.all()
        return render(self.request, self.template_name, self.context)


@method_decorator(login_required, name='dispatch')
class CourseEditorView(View):
    template_name = 'console/course-editor.html'
    context = {}
    form = CourseForm

    def get_object(self, uuid=None, is_update=False):
        try:
            if is_update:
                query = Course.objects.select_for_update().get(uuid=uuid)
            else:
                query = Course.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            query = None
        
        return query

    def get(self, request, uuid=None):
        queryset = self.get_object(uuid=uuid)

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        return render(self.request, self.template_name, self.context)

    @transaction.atomic()
    def post(self, request, uuid=None):
        queryset = self.get_object(uuid=uuid, is_update=True)
        form = self.form(request.POST, request.FILES, instance=queryset)

        if form.is_valid():
            f = form.save()
            return redirect('course_detail', uuid=f.uuid)

        self.context['form'] = form
        return render(self.request, self.template_name, self.context)


@method_decorator(login_required, name='dispatch')
class CourseQuizView(View):
    template_name = 'console/course-quiz.html'
    context = {}
    position = None

    def get_object(self, uuid=None, is_update=False):
        try:
            query = Course.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            query = None
        
        return query

    def get(self, request, uuid=None):
        self.position = request.GET.get('position')
        queryset = self.get_object(uuid=uuid)
        quiz_question = None
        quiz = None

        try:
            course_quiz = CourseQuiz.objects.get(course__uuid=uuid, position=self.position)
        except ObjectDoesNotExist:
            course_quiz = None
        
        if course_quiz:
            quiz = getattr(course_quiz, 'quiz', None)
            if quiz:
                quiz_question = quiz.quiz_question.all().order_by('sort')

        self.context['position'] = self.position
        self.context['queryset'] = queryset
        self.context['course_quiz'] = course_quiz
        self.context['quiz_question'] = quiz_question
        self.context['quiz'] = quiz
        return render(self.request, self.template_name, self.context)


@method_decorator(login_required, name='dispatch')
class ChapterView(View):
    template_name = 'console/course-chapter-editor.html'
    context = {}
    form = ChapterForm

    def get_object(self, uuid=None, is_update=False):
        try:
            if is_update:
                query = Chapter.objects.select_for_update().get(uuid=uuid)
            else:
                query = Chapter.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            query = None
        
        return query

    def get(self, request, uuid=None):
        queryset = self.get_object(uuid=uuid)
        material = None

        if queryset:
            material = queryset.material.all()

        self.context['queryset'] = queryset
        self.context['form'] = self.form(instance=queryset)
        self.context['material'] = material
        return render(self.request, self.template_name, self.context)

    @transaction.atomic()
    def post(self, request, uuid=None):
        queryset = self.get_object(uuid=uuid, is_update=True)
        form = self.form(request.POST, instance=queryset)

        if form.is_valid():
            f = form.save()
            return redirect('course_detail', uuid=queryset.course.uuid)

        self.context['form'] = form
        return render(self.request, self.template_name, self.context)
