from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from utils.generals import get_model

Course = get_model('training', 'Course')
CourseDate = get_model('training', 'CourseDate')
Enroll = get_model('training', 'Enroll')
Simulation = get_model('training', 'Simulation')
SimulationChapter = get_model('training', 'SimulationChapter')


class EnrollSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:enroll-detail',
                                               lookup_field='uuid', read_only=True)
    learner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    course_date = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseDate.objects.all())

    course_label = serializers.CharField(read_only=True, source='course.label')

    class Meta:
        model = Enroll
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _created = Enroll.objects.get_or_create(**validated_data)
        return instance

    def to_representation(self, value):
        ret = super().to_representation(value)
        simulation_dict = None

        try:
            simulation = value.simulation.filter(is_done=False).get()
            simulation_dict = {'uuid': simulation.uuid }
        except ObjectDoesNotExist:
            pass
        
        ret['simulation'] = simulation_dict
        return ret


class SimulationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:simulation-detail',
                                               lookup_field='uuid', read_only=True)
    learner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    enroll = serializers.SlugRelatedField(slug_field='uuid', queryset=Enroll.objects.all())
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())

    course_label = serializers.CharField(read_only=True, source='course.label')
    
    class Meta:
        model = Simulation
        fields = '__all__'

    def to_representation(self, value):
        ret = super().to_representation(value)
        quiz_before_dict = None
        quiz_after_dict = None

        # Get quiz before course
        try:
            quiz_before = value.simulation_quiz.get(course_quiz__position='before')
            quiz_before_dict = {
                'simulation_quiz_uuid': quiz_before.uuid,
                'course_quiz_uuid': quiz_before.course_quiz.uuid,
                'quiz_uuid': quiz_before.quiz.uuid,
                'label': quiz_before.quiz.label,
                'is_done': quiz_before.is_done,
            }
        except ObjectDoesNotExist:
            pass
        
        # Get quiz after course
        try:
            quiz_after = value.simulation_quiz.get(course_quiz__position='after')
            quiz_after_dict = {
                'simulation_quiz_uuid': quiz_after.uuid,
                'course_quiz_uuid': quiz_after.course_quiz.uuid,
                'quiz_uuid': quiz_after.quiz.uuid,
                'label': quiz_after.quiz.label,
                'is_done': quiz_after.is_done,
            }
        except ObjectDoesNotExist:
            pass

        ret['quiz'] = {
            'before': quiz_before_dict,
            'after': quiz_after_dict,
        }

        return ret
