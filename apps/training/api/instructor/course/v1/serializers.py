from rest_framework import serializers

from utils.generals import get_model
from utils.mixin.api import ListSerializerUpdateMappingField

Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourseQuiz')
Quiz = get_model('training', 'Quiz')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class CourseQuizListSerializer(ListSerializerUpdateMappingField, serializers.ListSerializer):
    pass


class CourseQuizSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=Quiz.objects.all())

    class Meta:
        model = CourseQuiz
        fields = '__all__'
        list_serializer_class = CourseQuizListSerializer
