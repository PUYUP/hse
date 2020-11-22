from rest_framework import serializers

from utils.generals import get_model
from utils.mixin.api import (
    DynamicFieldsModelSerializer, 
    ListSerializerUpdateMappingField, 
    WritetableFieldPutMethod
)

Question = get_model('training', 'Question')
QuizQuestion = get_model('training', 'QuizQuestion')
Choice = get_model('training', 'Choice')
Answer = get_model('training', 'Answer')
Simulation = get_model('training', 'Simulation')
SimulationQuiz = get_model('training', 'SimulationQuiz')
Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourseQuiz')
Quiz = get_model('training', 'Quiz')
User = get_model('person', 'User')


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['uuid', 'identifier', 'label', 'description']


class QuestionSerializer(serializers.ModelSerializer):
    choice = ChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = '__all__'


class QuizQuestionSerializer(serializers.ModelSerializer):
    quiz = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    question = QuestionSerializer(read_only=True)
    answer_uuid = serializers.UUIDField(read_only=True)
    answer_choice_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = QuizQuestion
        fields = '__all__'


class AnswerListSerializer(ListSerializerUpdateMappingField, serializers.ListSerializer):
    pass


class AnswerSerializer(DynamicFieldsModelSerializer, WritetableFieldPutMethod, serializers.ModelSerializer):
    learner = serializers.SlugRelatedField(slug_field='uuid', queryset=User.objects.all())
    simulation = serializers.SlugRelatedField(slug_field='uuid', queryset=Simulation.objects.all())
    simulation_quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=SimulationQuiz.objects.all())
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    course_quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseQuiz.objects.all())
    quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=Quiz.objects.all())
    question = serializers.SlugRelatedField(slug_field='uuid', queryset=Question.objects.all())
    choice = serializers.SlugRelatedField(slug_field='uuid', queryset=Choice.objects.all())

    class Meta:
        model = Answer
        fields = '__all__'
        list_serializer_class = AnswerListSerializer
