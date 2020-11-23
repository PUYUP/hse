from django.db import transaction
from django.db.models import Count, Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.expressions import Exists, OuterRef, Subquery
from django.http import request

from rest_framework import serializers

from utils.generals import get_model

from ...course.v1.serializers import CourseSerializer

Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourseQuiz')
Quiz = get_model('training', 'Quiz')
Chapter = get_model('training', 'Chapter')
CourseSession = get_model('training', 'CourseSession')
Enroll = get_model('training', 'Enroll')
EnrollSession = get_model('training', 'EnrollSession')
Simulation = get_model('training', 'Simulation')
SimulationChapter = get_model('training', 'SimulationChapter')
SimulationQuiz = get_model('training', 'SimulationQuiz')


class SimulationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:simulation-detail',
                                               lookup_field='uuid', read_only=True)
    learner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    enroll = serializers.SlugRelatedField(slug_field='uuid', queryset=Enroll.objects.all())
    enroll_session = serializers.SlugRelatedField(slug_field='uuid', queryset=EnrollSession.objects.all())
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    course_session = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseSession.objects.all())

    course_label = serializers.CharField(read_only=True, source='course.label')
    
    class Meta:
        model = Simulation
        fields = '__all__'

    def to_representation(self, value):
        ret = super().to_representation(value)
        quiz_survey_dict = None
        quiz_evaluate_dict = None

        # Get quiz survey course
        try:
            quiz_survey = value.simulation_quiz.get(course_quiz__position='survey')
            quiz_survey_dict = {
                'simulation_quiz_uuid': quiz_survey.uuid,
                'course_quiz_uuid': quiz_survey.course_quiz.uuid,
                'quiz_uuid': quiz_survey.quiz.uuid,
                'label': quiz_survey.quiz.label,
                'is_done': quiz_survey.is_done,
            }
        except ObjectDoesNotExist:
            pass
        
        # Get quiz evaluate course
        try:
            quiz_evaluate = value.simulation_quiz.get(course_quiz__position='evaluate')
            quiz_evaluate_dict = {
                'simulation_quiz_uuid': quiz_evaluate.uuid,
                'course_quiz_uuid': quiz_evaluate.course_quiz.uuid,
                'quiz_uuid': quiz_evaluate.quiz.uuid,
                'label': quiz_evaluate.quiz.label,
                'is_done': quiz_evaluate.is_done,
            }
        except ObjectDoesNotExist:
            pass

        ret['quiz'] = {
            'survey': quiz_survey_dict,
            'evaluate': quiz_evaluate_dict,
        }

        return ret


class SimulationQuizSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:simulationquiz-detail',
                                               lookup_field='uuid', read_only=True)

    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    simulation = serializers.SlugRelatedField(slug_field='uuid', queryset=Simulation.objects.all())
    course_quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseQuiz.objects.all())
    quiz = serializers.SlugRelatedField(slug_field='uuid', queryset=Quiz.objects.all())

    true_answer = serializers.IntegerField(read_only=True)
    false_answer = serializers.IntegerField(read_only=True)
    position = serializers.CharField(read_only=True, source='course_quiz.position')

    class Meta:
        model = SimulationQuiz
        fields = '__all__'


class SimulationRetrieveSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_session = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseSession.objects.all())
    simulation_quiz = SimulationQuizSerializer(many=True, read_only=True)

    class Meta:
        model = Simulation
        fields = '__all__'


class SimulationChapterSerializer(serializers.ModelSerializer):
    simulation = serializers.SlugRelatedField(slug_field='uuid', queryset=Simulation.objects.all())
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    course_session = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseSession.objects.all())
    chapter = serializers.SlugRelatedField(slug_field='uuid', queryset=Chapter.objects.all())

    class Meta:
        model = SimulationChapter
        fields = '__all__'


class EnrollSessionSerializer(serializers.ModelSerializer):
    course_session = serializers.SlugRelatedField(slug_field='uuid', queryset=CourseSession.objects.all())
    simulation = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EnrollSession
        fields = ['uuid', 'course_session', 'simulation', 'create_date']

    def get_simulation(self, obj):
        quiz = Quiz.objects \
            .filter(simulation_quiz__simulation__uuid=OuterRef('uuid')) \
            .annotate(
                true_answer_survey=Count(
                    'simulation_quiz__answer',
                    distinct=True,
                    filter=Q(simulation_quiz__answer__is_true=True, simulation_quiz__answer__course_quiz__position='survey')
                ),
                true_answer_evaluate=Count(
                    'simulation_quiz__answer',
                    distinct=True,
                    filter=Q(simulation_quiz__answer__is_true=True, simulation_quiz__answer__course_quiz__position='evaluate')
                ),
                total_survey_question=Count('quiz_question', distinct=True),
                total_evaluate_question=Count('quiz_question', distinct=True)
            )

        simulation_objs = obj.simulation.prefetch_related('course', 'enroll') \
            .select_related('course', 'enroll') \
            .annotate(
                quiz_survey_true_answer=Subquery(quiz.filter(course_quiz__position='survey').values('true_answer_survey')[:1]),
                quiz_evaluate_true_answer=Subquery(quiz.filter(course_quiz__position='evaluate').values('true_answer_evaluate')[:1]),
                total_survey_question=Subquery(quiz.filter(course_quiz__position='survey').values('total_survey_question')[:1]),
                total_evaluate_question=Subquery(quiz.filter(course_quiz__position='evaluate').values('total_evaluate_question')[:1])
            ) \
            .order_by('-repeated')

        simulation_list = []
        for item in simulation_objs:
            quiz_survey_score = 0
            quiz_evaluate_score = 0

            if item.total_survey_question:
                quiz_survey_score = int(100 /  item.total_survey_question * item.quiz_survey_true_answer)

            if item.total_evaluate_question:
                quiz_evaluate_score = int(100 /  item.total_evaluate_question * item.quiz_evaluate_true_answer)

            d = {
                'uuid': item.uuid,
                'repeated': item.repeated,
                'create_date': item.create_date,
                'repeated': item.repeated,
                'is_done': item.is_done,
                'total_survey_question': item.total_survey_question,
                'total_evaluate_question': item.total_evaluate_question,
                'quiz_survey_true_answer': item.quiz_survey_true_answer,
                'quiz_evaluate_true_answer': item.quiz_evaluate_true_answer,
                'quiz_survey_score': quiz_survey_score,
                'quiz_evaluate_score': quiz_evaluate_score,
            }

            simulation_list.append(d)
        return simulation_list


class EnrollSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:enroll-detail',
                                               lookup_field='uuid', read_only=True)
    learner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())
    enroll_session = EnrollSessionSerializer(many=True)

    course_label = serializers.CharField(read_only=True, source='course.label')
    course_cover = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Enroll
        fields = '__all__'

    def get_course_cover(self, obj):
        request = self.context.get('request')
        cover = obj.course.cover

        if cover:
            cover_url = cover.url
            return request.build_absolute_uri(cover_url)
        return None

    @transaction.atomic
    def create(self, validated_data):
        enroll_session = validated_data.pop('enroll_session', None)
        instance, _created = Enroll.objects.get_or_create(**validated_data)

        # Create enroll_session
        for item in enroll_session:
            enroll_session_obj, _created = EnrollSession.objects.get_or_create(enroll=instance, **item)

        return instance
