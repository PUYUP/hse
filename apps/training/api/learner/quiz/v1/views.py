from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction, IntegrityError
from django.db.models import OuterRef, Subquery
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .serializers import AnswerSerializer, QuizQuestionSerializer

from utils.generals import get_model
from utils.pagination import build_result_pagination

QuizQuestion = get_model('training', 'QuizQuestion')
Answer = get_model('training', 'Answer')
SimulationQuiz = get_model('training', 'SimulationQuiz')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class QuizQuestionApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def initialize_request(self, request, *args, **kwargs):
        self.simulation_uuid = None
        self.position = None

        return super().initialize_request(request, *args, **kwargs)

    def queryset(self):
        answer = Answer.objects.filter(question__uuid=OuterRef('question__uuid'),
                                       quiz__uuid=OuterRef('quiz__uuid'),
                                       simulation__uuid=self.simulation_uuid,
                                       course_quiz__position=self.position)

        query = QuizQuestion.objects.prefetch_related('question', 'quiz') \
            .select_related('question', 'quiz') \
            .annotate(
                answer_uuid=Subquery(answer[:1].values('uuid')),
                answer_choice_uuid=Subquery(answer[:1].values('choice__uuid'))
            ) \
            .order_by('sort')

        return query

    def get_object(self, uuid=None):
        try:
            queryset = self.queryset().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        return queryset

    def list(self, request, format=None):
        context = {'request': request}
        quiz_uuid = request.query_params.get('quiz_uuid', None)
        
        self.simulation_uuid = request.query_params.get('simulation_uuid', None)
        self.position = request.query_params.get('position', None)

        try:
            queryset = self.queryset().filter(quiz__uuid=quiz_uuid)
        except ValidationError as e:
            raise NotAcceptable(detail=repr(e))
        
        _PAGINATOR.default_limit = 1

        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = QuizQuestionSerializer(queryset_paginator, many=True, context=context)
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)

        return Response(pagination_result, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}
        queryset = self.get_object(uuid=uuid)
        serialzer = QuizQuestionSerializer(queryset, many=False, context=context)
        
        return Response(serialzer.data, status=response_status.HTTP_200_OK)


class AnswerApiView(viewsets.ViewSet):
    """

        [
            {
                "learner": "bada89b5-7ee0-45bc-94f1-6c37a935c125",
                "simulation": "d1488959-beab-4184-8db6-81d0f5840ab8",
                "course": "41f323f0-5f6e-428a-9f93-19c2ff76d106",
                "course_quiz": "ff8d6052-7444-43c6-a94d-7f3f089fafb7",
                "quiz": "0e37b806-7e74-4312-9b0e-1ae06eb39506",
                "question": "76a75a49-6294-40ca-a1cc-6567550f06c4",
                "choice": "a06b3051-26d1-4bbd-a10d-26cf09c77a90"
            }
        ]

    """
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self):
        qs = Answer.objects.prefetch_related('learner', 'simulation', 'course',
                                             'course_quiz', 'quiz', 'question',
                                             'choice') \
            .select_related('learner', 'simulation', 'course', 'course_quiz',
                            'quiz', 'question', 'choice')
        return qs

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = AnswerSerializer(data=request.data, many=False, context=context)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except (ValidationError, IntegrityError) as e:
                raise NotAcceptable(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    @method_decorator(never_cache)
    @transaction.atomic
    def put(self, request, format=None):
        context = {'request': request}
        update_fields = ['learner', 'simulation', 'course', 'course_quiz', 'quiz',
                         'question', 'choice']  # related field to select_related in queryset
        update_uuids = [item.get('uuid') for item in request.data]

        # Collect fields affect for updated
        for item in request.data:
            update_fields.extend(list(item.keys()))
        update_fields = list(dict.fromkeys(update_fields))
    
        queryset = self.queryset().filter(uuid__in=update_uuids).only(*update_fields)
        serializer = AnswerSerializer(queryset, data=request.data, many=True,
                                      context=context, fields_used=update_fields)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                
                # Prepare mark simulation quiz done
                simulation = None
                quiz = None
                course = None
                course_quiz = None
                simulation_quiz_obj = None

                for d in serializer.data:
                    simulation = dict(d).get('simulation')
                    quiz = dict(d).get('quiz')
                    course = dict(d).get('course')
                    course_quiz = dict(d).get('course_quiz')
                    break
                
                try:
                    simulation_quiz_obj = SimulationQuiz.objects \
                        .get(simulation__uuid=simulation, quiz__uuid=quiz,
                             course__uuid=course, course_quiz__uuid=course_quiz)
                except ObjectDoesNotExist:
                    pass
                
                if simulation_quiz_obj:
                    simulation_quiz_obj.is_done = True
                    simulation_quiz_obj.save()

            except (ValidationError, Exception) as e:
                raise NotAcceptable(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)
