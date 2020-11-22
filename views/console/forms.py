from django.forms import ModelForm

from utils.generals import get_model

Course = get_model('training', 'Course')


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['category', 'label', 'description', 'cover']
