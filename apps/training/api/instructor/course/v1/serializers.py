from rest_framework import serializers

from utils.generals import get_model

Course = get_model('training', 'Course')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
