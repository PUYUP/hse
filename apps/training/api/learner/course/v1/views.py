import datetime
from dateutil import parser

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Prefetch, Count, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from utils.generals import get_model
from utils.pagination import build_result_pagination

from .serializers import CourseSerializer, CourseQuizSerializer

Course = get_model('training', 'Course')
CourseQuiz = get_model('training', 'CourseQuiz')
CourseDate = get_model('training', 'CourseDate')
Quiz = get_model('training', 'Quiz')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class CourseApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self, start_date=None):
        if start_date:
            dt = parser.parse(start_date)
            dt_format = dt.strftime('%Y-%m-%d')

            q_start_date = Q(course_date__start_date__date=dt_format)
            q_course_date = Q(start_date__date=dt_format)
        else:
            today = timezone.datetime.today().strftime('%Y-%m-%d')
            q_start_date = Q(course_date__start_date__gte=today)
            q_course_date = Q(start_date__gte=today)
        
        course_date_objs = CourseDate.objects.filter(q_course_date).order_by('start_date')

        qs = Course.objects \
            .prefetch_related('creator', 'category', Prefetch('course_date', queryset=course_date_objs)) \
            .select_related('creator', 'category') \
            .annotate(
                course_date_count=Count(
                    'course_date', 
                    filter=q_start_date,
                    distinct=True
                )
            ) \
            .filter(is_active=True, course_date_count__gt=0)

        return qs

    def list(self, request, format=None):
        context = {'request': request}
        start_date = request.query_params.get('start_date', None)

        queryset = self.queryset(start_date=start_date)
        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = CourseSerializer(queryset_paginator, many=True, context=context)
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)

        return Response(pagination_result, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}
    
        try:
            queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))
    
        serializer = CourseSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)


class CourseQuizApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self):
        qs = CourseQuiz.objects \
            .prefetch_related('course', 'quiz') \
            .select_related('course', 'quiz')

        return qs

    def list(self, request, format=None):
        context = {'request': request}
        course_uuid = request.query_params.get('course_uuid', None)
        position = request.query_params.get('position', None)

        if not course_uuid or not position:
            raise NotAcceptable(detail=_("Param course_uuid and position required"))

        queryset = self.queryset().filter(position=position, course__uuid=course_uuid)
        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = CourseQuizSerializer(queryset_paginator, many=True, context=context)
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)

        return Response(pagination_result, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}
    
        try:
            queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))
    
        serializer = CourseQuizSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
