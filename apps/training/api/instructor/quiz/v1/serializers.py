from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from rest_framework import serializers

from utils.generals import get_model

Question = get_model('training', 'Question')
Choice = get_model('training', 'Choice')
Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourSeQuiz')
Quiz = get_model('training', 'Quiz')
QuizQuestion = get_model('training', 'QuizQuestion')


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['identifier', 'label', 'description']


class QuestionListSerializer(serializers.ListSerializer):
    @transaction.atomic
    def update(self, instance, validated_data):
        # Maps for uuid->instance and uuid->data item.
        obj_mapping = {obj.uuid: obj for obj in instance}
        data_mapping = {item.get('uuid', index): item for index, item in enumerate(validated_data)}

        # Perform creations and updates.
        ret = []
        for obj_uuid, data in data_mapping.items():
            obj = obj_mapping.get(obj_uuid, None)

            if obj is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(obj, data))

        # Perform deletions.
        for obj_uuid, obj in obj_mapping.items():
            if obj_uuid not in data_mapping:
                obj.delete()

        return ret


class QuestionSerializer(serializers.ModelSerializer):
    choice = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = '__all__'
        list_serializer_class = QuestionListSerializer

    @transaction.atomic
    def create(self, validated_data):
        duration = 10
        position = self.context.get('position')
        course_uuid = self.context.get('course_uuid')

        try:
            course_obj = Course.objects.get(uuid=course_uuid)
        except ObjectDoesNotExist:
            course_obj = None

        # Create Quiz
        label = '{} {}'.format(course_obj.label, position)
        quiz_obj, _quiz_created = Quiz.objects.get_or_create(label=label)

        choice = validated_data.pop('choice')
        instance = Question.objects.create(**validated_data)

        for item in choice:
            Choice.objects.create(**item, question=instance)
        
        instance.refresh_from_db()

        # Append Question to Quiz
        _quiz_question_obj = QuizQuestion.objects.create(quiz=quiz_obj, question=instance)

        # Append Quiz to Course
        course_quiz_obj = CourseQuiz.objects.create(course=course_obj, quiz=quiz_obj,
                                                    position=position, duration=duration)
        return instance
