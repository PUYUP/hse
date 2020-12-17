from django.db import transaction, IntegrityError
from django.db.models import Count, Q, F, OuterRef, Subquery
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action

from utils.generals import get_model, make_cert
from utils.pagination import build_result_pagination

from .serializers import (
    EnrollSerializer, SimulationChapterSerializer, SimulationRetrieveSerializer, 
    SimulationSerializer, 
    SimulationQuizSerializer
)

Enroll = get_model('training', 'Enroll')
Simulation = get_model('training', 'Simulation')
SimulationChapter = get_model('training', 'SimulationChapter')
SimulationQuiz = get_model('training', 'SimulationQuiz')
SimulationAttachment = get_model('training', 'SimulationAttachment')
Quiz = get_model('training', 'Quiz')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class EnrollApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self):
        query = Enroll.objects \
            .prefetch_related('learner', 'course', 'enroll_session') \
            .select_related('learner', 'course')

        return query

    def get_object(self, uuid=None):
        try:
            queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))

        return queryset

    def list(self, request, format=None):
        context = {'request': request}
        course_uuid = request.query_params.get('course_uuid')
        user_uuid = request.query_params.get('user_uuid')
        queryset = self.queryset()

        if course_uuid:
            queryset = queryset.filter(course__uuid=course_uuid)

        if user_uuid:
            queryset = queryset.filter(learner__uuid=user_uuid)
        else:
            queryset = queryset.filter(learner__uuid=request.user.uuid)

        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = EnrollSerializer(queryset_paginator, many=True, context=context)
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)

        return Response(pagination_result, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}
        queryset = self.get_object(uuid=uuid)
        serializer = EnrollSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = EnrollSerializer(data=request.data, context=context)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except (ValidationError, IntegrityError) as e:
                raise NotAcceptable(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    @method_decorator(never_cache)
    @transaction.atomic
    def destroy(self, request, uuid=None, format=None):
        queryset = self.get_object(uuid=uuid)

        if queryset.learner.uuid != request.user.uuid:
            raise NotAcceptable(detail=_("Restricted!"))

        queryset.delete()
        return Response({'detail': _("Delete success!")},
                        status=response_status.HTTP_204_NO_CONTENT)


class SimulationApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self):
        qs = Simulation.objects \
            .prefetch_related('learner', 'enroll', 'enroll_session', 'course', 'course__chapter', 'course_session') \
            .select_related('learner', 'enroll', 'enroll_session', 'course', 'course_session') \
            .annotate(
                chapter_done_count=Count('simulation_chapter', distinct=True, filter=Q(simulation_chapter__is_done=True)),
                chapter_total_count=Count('course__chapter', distinct=True)
            ) \
            .filter(learner__id=self.request.user.id)

        return qs

    def get_object(self, uuid=None, is_update=False):
        try:
            if is_update:
                queryset = self.queryset().select_for_update().get(uuid=uuid)
            else:
                queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))

        return queryset

    def list(self, request, format=None):
        context = {'request': request}
        enroll_uuid = request.query_params.get('enroll_uuid', None)
        if enroll_uuid is None:
            raise NotAcceptable(detail=_("Param enroll_uuid required"))

        try:
            queryset = self.queryset().filter(enroll__uuid=enroll_uuid)
        except ValidationError as e:
            raise NotAcceptable(detail=repr(e))

        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = SimulationSerializer(queryset_paginator, many=True, context=context)
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)

        return Response(pagination_result, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request, 'simulation_uuid': uuid}
        queryset = self.get_object(uuid=uuid)
        serializer = SimulationRetrieveSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = SimulationSerializer(data=request.data, context=context)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except (ValidationError, IntegrityError) as e:
                raise NotAcceptable(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    @method_decorator(never_cache)
    @transaction.atomic
    def partial_update(self, request, uuid=None, format=None):
        context = {'request': request}
        queryset = self.get_object(uuid=uuid, is_update=True)
        serializer = SimulationSerializer(queryset, data=request.data, partial=True, context=context)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    @method_decorator(never_cache)
    @transaction.atomic
    def destroy(self, request, uuid=None, format=None):
        queryset = self.get_object(uuid=uuid)

        if queryset.learner.uuid != request.user.uuid:
            raise NotAcceptable(detail=_("Restricted!"))

        queryset.delete()
        return Response({'detail': _("Delete success!")},
                        status=response_status.HTTP_204_NO_CONTENT)

    # Sub-action create certificate
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated],
            url_path='generate-certificate', url_name='generate_certificate')
    def generate_certificate(self, request, uuid=None):
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
        
        simulation_obj = Simulation.objects.prefetch_related('course', 'enroll') \
            .select_related('course', 'enroll') \
            .annotate(
                quiz_survey_true_answer=Subquery(quiz.filter(course_quiz__position='survey').values('true_answer_survey')[:1]),
                quiz_evaluate_true_answer=Subquery(quiz.filter(course_quiz__position='evaluate').values('true_answer_evaluate')[:1]),
                total_survey_question=Subquery(quiz.filter(course_quiz__position='survey').values('total_survey_question')[:1]),
                total_evaluate_question=Subquery(quiz.filter(course_quiz__position='evaluate').values('total_evaluate_question')[:1])
            ) \
            .get(uuid=uuid)
        
        quiz_survey_score = 0
        quiz_evaluate_score = 0

        if simulation_obj.total_survey_question:
            quiz_survey_score = int(100 /  simulation_obj.total_survey_question * simulation_obj.quiz_survey_true_answer)

        if simulation_obj.total_evaluate_question:
            quiz_evaluate_score = int(100 /  simulation_obj.total_evaluate_question * simulation_obj.quiz_evaluate_true_answer)

        d = {
            'total_survey_question': simulation_obj.total_survey_question,
            'total_evaluate_question': simulation_obj.total_evaluate_question,
            'quiz_survey_true_answer': simulation_obj.quiz_survey_true_answer,
            'quiz_evaluate_true_answer': simulation_obj.quiz_evaluate_true_answer,
            'quiz_survey_score': quiz_survey_score,
            'quiz_evaluate_score': quiz_evaluate_score,
        }

        certificate_obj, _created = SimulationAttachment.objects.get_or_create(simulation=simulation_obj, identifier='certificate', file='cert_file')
        qrcode_obj, _created = SimulationAttachment.objects.get_or_create(simulation=simulation_obj, identifier='qrcode', file='qr_file')

        date_fmt = simulation_obj.create_date.strftime('%A, %d %B %Y')
        person_name = simulation_obj.learner.first_name
        score = quiz_evaluate_score
        course_name = simulation_obj.course.label
        qrcode_text = request.build_absolute_uri(reverse('certificate_detail', kwargs={'uuid': certificate_obj.uuid}))
        
        cert = make_cert(person_name=person_name, date_fmt=date_fmt, score=str(score), course_name=course_name,
                         qrcode_text=qrcode_text, instance=simulation_obj)
        cert_file = cert['certificate'].split('media/')[1]
        qr_file = cert['qrcode'].split('media/')[1]

        certificate_obj.file = cert_file
        certificate_obj.save(update_fields=['file'])

        qrcode_obj.file = qr_file
        qrcode_obj.save(update_fields=['file'])

        return Response(
            {
                'detail': _("Certificate created!"),
                'certificate_file': request.build_absolute_uri(certificate_obj.file.url),
            }, 
            status=response_status.HTTP_200_OK
        )


class SimulationChapterApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self):
        qs = SimulationChapter.objects \
            .prefetch_related('simulation', 'course', 'course_session', 'chapter') \
            .select_related('simulation', 'course', 'course_session')

        return qs

    def get_object(self, uuid=None, is_update=False):
        try:
            if is_update:
                queryset = self.queryset().select_for_update().get(uuid=uuid)
            else:
                queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))

        return queryset

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = SimulationChapterSerializer(data=request.data, context=context)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except (ValidationError, IntegrityError) as e:
                raise NotAcceptable(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    @method_decorator(never_cache)
    @transaction.atomic
    def partial_update(self, request, uuid=None, format=None):
        context = {'request': request}
        queryset = self.get_object(uuid=uuid, is_update=True)
        serializer = SimulationChapterSerializer(queryset, data=request.data, partial=True, context=context)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)


class SimulationQuizApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self):
        qs = SimulationQuiz.objects \
            .prefetch_related('simulation', 'course_quiz', 'course', 'quiz', 'answer') \
            .select_related('simulation', 'course_quiz', 'course', 'quiz') \
            .filter(simulation__learner__id=self.request.user.id)

        return qs

    def get_object(self, uuid=None):
        try:
            queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))

        return queryset

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}
    
        queryset = self.queryset() \
            .annotate(
                true_answer=Count('answer', filter=Q(answer__is_true=True)),
                false_answer=Count('answer', filter=Q(answer__is_true=False))
            ) \
            .get(uuid=uuid)

        serializer = SimulationQuizSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = SimulationQuizSerializer(data=request.data, context=context)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except (ValidationError, IntegrityError) as e:
                raise NotAcceptable(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)
