from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction

from utils.generals import get_model
from .forms import CourseForm

Course = get_model('training', 'Course')


@method_decorator(login_required, name='dispatch')
class CourseView(View):
    template_name = 'console/course.html'
    context = {}

    def get_objects(self):
        objs = Course.objects.prefetch_related('category') \
            .select_related('category') \
            .all()

        return objs

    def get(self, request):
        objs = self.get_objects()

        self.context['objs'] = objs
        return render(self.request, self.template_name, self.context)


@method_decorator(login_required, name='dispatch')
class CourseDetailView(View):
    template_name = 'console/course-detail.html'
    context = {}

    def get(self, request, uuid=None):
        try:
            obj = Course.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            obj = None
        
        self.context['obj'] = obj
        self.context['chapter'] = obj.chapter.all()
        return render(self.request, self.template_name, self.context)


@method_decorator(login_required, name='dispatch')
class CourseEditorView(View):
    template_name = 'console/course-editor.html'
    context = {}
    form = CourseForm

    def get_object(self, uuid=None, is_update=False):
        try:
            if is_update:
                obj = Course.objects.select_for_update().get(uuid=uuid)
            else:
                obj = Course.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            obj = None
        
        return obj

    def get(self, request, uuid=None):
        obj = self.get_object(uuid=uuid)

        self.context['form'] = self.form(instance=obj)
        self.context['obj'] = obj
        return render(self.request, self.template_name, self.context)

    @transaction.atomic()
    def post(self, request, uuid=None):
        obj = self.get_object(uuid=uuid, is_update=True)
        form = self.form(request.POST, request.FILES, instance=obj)

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
            obj = Course.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            obj = None
        
        return obj

    def get(self, request, uuid=None):
        self.position = request.GET.get('position')
        obj = self.get_object(uuid=uuid)
        
        self.context['position'] = self.position
        self.context['obj'] = obj
        return render(self.request, self.template_name, self.context)
