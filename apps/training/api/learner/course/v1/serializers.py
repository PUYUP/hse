from django.core.exceptions import ObjectDoesNotExist
from utils.mixin.api import DynamicFieldsModelSerializer
from rest_framework import serializers

from utils.generals import get_model

Course = get_model('training', 'Course')
Chapter = get_model('training', 'Chapter')
Material = get_model('training', 'Material')
CourseQuiz = get_model('training', 'CourseQuiz')
CourseSession = get_model('training', 'CourseSession')
Quiz = get_model('training', 'Quiz')


class CourseSessionListSerializer(serializers.ListSerializer):
    def to_representation(self, value):
        value = value.all()[:1]
        return super().to_representation(value)


class CourseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSession
        fields = ['uuid', 'start_date', 'end_date',]
        list_serializer_class = CourseSessionListSerializer


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['uuid', 'type', 'media', 'text', 'mime', 'description']


class ChapterSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True, many=True)
    course = serializers.SlugRelatedField(slug_field='uuid', read_only=True)

    class Meta:
        model = Chapter
        fields = ['uuid', 'material', 'label', 'number', 'sort_order', 'description', 'course']

    def to_representation(self, value):
        ret = super().to_representation(value)
        simulation_uuid = self.context.get('simulation_uuid') # from SimulationApiView context

        if simulation_uuid:
            simulation_chapter_obj = None

            try:
                simulation_chapter_obj = value.simulation_chapter.get(simulation__uuid=simulation_uuid)
            except ObjectDoesNotExist:
                pass
            
            if simulation_chapter_obj:
                ret['simulation_chapter_uuid'] = simulation_chapter_obj.uuid
                ret['simulation_chapter_is_done'] = simulation_chapter_obj.is_done
        return ret


class CourseQuizSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:coursequiz-detail',
                                               lookup_field='uuid', read_only=True)

    quiz = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    course = serializers.SlugRelatedField(slug_field='uuid', read_only=True)

    class Meta:
        model = CourseQuiz
        fields = '__all__'


class CourseSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:course-detail',
                                               lookup_field='uuid', read_only=True)

    chapter = ChapterSerializer(read_only=True, many=True)
    course_session = CourseSessionSerializer(read_only=True, many=True)
    course_quiz = CourseQuizSerializer(many=True, read_only=True)
    enroll_uuid = serializers.CharField(read_only=True)
    is_enrolled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
