from django.contrib import admin

from utils.generals import get_model

Question = get_model('training', 'Question')
Choice = get_model('training', 'Choice')
Quiz = get_model('training', 'Quiz')
QuizQuestion = get_model('training', 'QuizQuestion')
Category = get_model('training', 'Category')
Course = get_model('training', 'Course')
CourseSession = get_model('training', 'CourseSession')
Chapter = get_model('training', 'Chapter')
Material = get_model('training', 'Material')
CourseQuiz = get_model('training', 'CourseQuiz')
Enroll = get_model('training', 'Enroll')
EnrollSession = get_model('training', 'EnrollSession')
Simulation = get_model('training', 'Simulation')
SimulationChapter = get_model('training', 'SimulationChapter')
SimulationQuiz = get_model('training', 'SimulationQuiz')
Answer = get_model('training', 'Answer')
SimulationAttachment = get_model('training', 'SimulationAttachment')

from .forms import ChoiceInlineForm


class ChoiceInline(admin.StackedInline):
    model = Choice
    formset = ChoiceInlineForm
    min_num = 2
    max_num = 4


class QuestionExtend(admin.ModelAdmin):
    model = Question
    inlines = [ChoiceInline,]


class ChapterInline(admin.StackedInline):
    model = Chapter


class CourseSessionInline(admin.StackedInline):
    model = CourseSession


class CourseExtend(admin.ModelAdmin):
    model = Course
    inlines = [ChapterInline, CourseSessionInline,]


class MaterialInline(admin.StackedInline):
    model = Material

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'course':
            parent_id = request.resolver_match.kwargs.get('object_id')
            parent_model = self.parent_model
            parent_obj = parent_model.objects.get(id=parent_id)
            course_id = parent_obj.course.id

            kwargs['initial'] = course_id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ChapterExtend(admin.ModelAdmin):
    model = Chapter
    list_display = ('label', 'course', 'sort_order',)
    inlines = [MaterialInline,]


class EnrollSessionInline(admin.StackedInline):
    model = EnrollSession


class EnrollExtend(admin.ModelAdmin):
    model = Enroll
    inlines = [EnrollSessionInline,]


admin.site.register(Question, QuestionExtend)
admin.site.register(Choice)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(Category)
admin.site.register(Course, CourseExtend)
admin.site.register(Chapter, ChapterExtend)
admin.site.register(Material)
admin.site.register(CourseQuiz)
admin.site.register(Enroll, EnrollExtend)
admin.site.register(Simulation)
admin.site.register(SimulationChapter)
admin.site.register(SimulationQuiz)
admin.site.register(Answer)
admin.site.register(SimulationAttachment)
