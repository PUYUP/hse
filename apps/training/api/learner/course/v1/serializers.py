from rest_framework import serializers

from utils.generals import get_model

Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourseQuiz')
CourseDate = get_model('training', 'CourseDate')
Quiz = get_model('training', 'Quiz')


class CourseDateListSerializer(serializers.ListSerializer):
    def to_representation(self, value):
        value = value.all()[:1]
        return super().to_representation(value)


class CourseDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDate
        fields = ['uuid', 'start_date', 'end_date',]
        list_serializer_class = CourseDateListSerializer


class CourseSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:course-detail',
                                               lookup_field='uuid', read_only=True)

    course_date = CourseDateSerializer(read_only=True, many=True)

    class Meta:
        model = Course
        fields = '__all__'


class CourseQuizSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='training_api:learner:coursequiz-detail',
                                               lookup_field='uuid', read_only=True)

    quiz = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    course = serializers.SlugRelatedField(slug_field='uuid', read_only=True)

    class Meta:
        model = CourseQuiz
        fields = '__all__'
