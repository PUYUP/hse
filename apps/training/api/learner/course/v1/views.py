from dateutil import parser
from calendar import monthrange

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Prefetch, Count, Q, Exists, OuterRef, Subquery
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from utils.generals import get_model
from utils.pagination import build_result_pagination

from .serializers import ChapterSerializer, CourseSerializer, CourseQuizSerializer

Course = get_model('training', 'Course')
Chapter = get_model('training', 'Chapter')
CourseQuiz = get_model('training', 'CourseQuiz')
CourseSession = get_model('training', 'CourseSession')
Quiz = get_model('training', 'Quiz')
Enroll = get_model('training', 'Enroll')
SimulationChapter = get_model('training', 'SimulationChapter')
Simulation = get_model('training', 'Simulation')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class CourseApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def queryset(self, start_date=None, is_single=False):
        if start_date:
            dt = parser.parse(start_date)
            dt_format = dt.strftime('%Y-%m-%d')

            year = dt.strftime('%Y')
            month = dt.strftime('%m')
            day_start, day_end = monthrange(int(year), int(month))
            day_start += 1
            
            date_end = parser.parse('{}-{}-{}'.format(year, month, day_end))
            date_end_format = date_end.strftime('%Y-%m-%d')

            q_start_date = Q(course_session__start_date__range=(dt_format, date_end_format))
            q_course_session = Q(start_date__range=(dt_format, date_end_format))
        else:
            today = timezone.datetime.today()
            year = today.strftime('%Y')
            month = today.strftime('%m')
            day_start, day_end = monthrange(int(year), int(month))
            day_start += 1

            date_end = parser.parse('{}-{}-{}'.format(9999, month, day_end))
            date_end_format = date_end.strftime('%Y-%m-%d')
            date_start = parser.parse('{}-{}-{}'.format(1990, month, day_start))
            date_start_format = date_start.strftime('%Y-%m-%d')

            q_start_date = Q(course_session__start_date__range=(date_start_format, date_end_format))
            q_course_session = Q(start_date__range=(date_start_format, date_end_format))
        
        course_session_objs = CourseSession.objects.filter(q_course_session).order_by('start_date')
        enroll_obj = Enroll.objects.filter(course__uuid=OuterRef('uuid'), learner__id=self.request.user.id)
        simulation = Simulation.objects.filter(course__uuid=OuterRef('uuid'), learner__id=self.request.user.id,
                                               is_done=False)

        if (is_single):
            course_session_objs = None
            q_start_date = Q()

        qs = Course.objects \
            .prefetch_related('creator', 'category', 'chapter', Prefetch('course_session', queryset=course_session_objs)) \
            .select_related('creator', 'category') \
            .annotate(
                course_session_count=Count(
                    'course_session', 
                    filter=q_start_date,
                    distinct=True
                ),
                enroll_uuid=Subquery(enroll_obj.values('uuid')),
                is_enrolled=Exists(enroll_obj),
                last_simulation_uuid=Subquery(simulation.values('uuid')[:1])
            ) \
            .filter(is_active=True, course_session_count__gt=0)
    
        return qs

    def list(self, request, format=None):
        context = {'request': request}
        start_date = request.query_params.get('start_date', None)
        keyword = request.query_params.get('keyword', None)
        category_uuid = request.query_params.get('category_uuid', None)

        queryset = self.queryset(start_date=start_date).order_by('-create_date')
        
        if keyword:
            queryset = queryset.filter(label__icontains=keyword)

        if category_uuid:
            queryset = queryset.filter(category__uuid=category_uuid)

        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = CourseSerializer(queryset_paginator, many=True, context=context,
                                      fields_used=['url', 'uuid', 'enroll_uuid', 'is_enrolled',
                                                   'label', 'course_session', 'cover'])
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)

        return Response(pagination_result, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}

        try:
            queryset = self.queryset(is_single=True).get(uuid=uuid)
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


class ChapterApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def initialize_request(self, request, *args, **kwargs):
        self.simulation_uuid = request.GET.get('simulation_uuid')
        return super().initialize_request(request, *args, **kwargs)

    def queryset(self):
        qs = Chapter.objects \
            .prefetch_related('course') \
            .select_related('course')

        return qs

    def list(self, request, format=None):
        context = {'request': request}
        return Response({}, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        context = {'request': request}
    
        try:
            queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))
    
        serializer = ChapterSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
