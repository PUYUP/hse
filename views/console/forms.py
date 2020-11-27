from django.forms import ModelForm

from utils.generals import get_model

Course = get_model('training', 'Course')
Chapter = get_model('training', 'Chapter')


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['category', 'label', 'description', 'cover']


class ChapterForm(ModelForm):
    class Meta:
        model = Chapter
        fields = ['label']
