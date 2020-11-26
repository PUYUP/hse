from rest_framework import serializers

from utils.generals import get_model
from utils.mixin.api import ListSerializerUpdateMappingField, WritetableFieldPutMethod

Question = get_model('training', 'Question')
Choice = get_model('training', 'Choice')
Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourSeQuiz')
Quiz = get_model('training', 'Quiz')
QuizQuestion = get_model('training', 'QuizQuestion')


class ChoiceListSerializer(ListSerializerUpdateMappingField, serializers.ListSerializer):
    pass


class ChoiceSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)
    question = serializers.SlugRelatedField(slug_field='uuid', queryset=Question.objects.all())

    class Meta:
        model = Choice
        fields = '__all__'
        list_serializer_class = ChoiceListSerializer


class QuestionListSerializer(ListSerializerUpdateMappingField, serializers.ListSerializer):
    pass


class QuestionSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = Question
        fields = '__all__'
        list_serializer_class = QuestionListSerializer


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'


class QuizQuestionListSerializer(ListSerializerUpdateMappingField, serializers.ListSerializer):
    pass


class QuizQuestionSerializer(serializers.ModelSerializer):
    quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=Quiz.objects.all())
    question = serializers.SlugRelatedField(slug_field='uuid', queryset=Question.objects.all())

    class Meta:
        model = QuizQuestion
        fields = '__all__'
        list_serializer_class =  QuizQuestionListSerializer
