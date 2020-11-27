from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from utils.generals import get_model
from .serializers import CourseQuizSerializer, CourseSerializer

CourseQuiz = get_model('training', 'CourseQuiz')


class CourseApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = CourseSerializer(data=request.data, context=context)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)


class CourseQuizApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def queryset(self):
        query = CourseQuiz.objects \
            .prefetch_related('quiz', 'course') \
            .select_related('quiz', 'course')
    
        return query

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = CourseQuizSerializer(data=request.data, context=context)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    @method_decorator(never_cache)
    @transaction.atomic
    def put(self, request, format=None):
        update_fields = ['quiz', 'course']
        update_uuids = [item.get('uuid') for item in request.data]

        # Collect fields affect for updated
        for item in request.data:
            update_fields.extend(list(item.keys()))

        update_fields = list(dict.fromkeys(update_fields))
        queryset = self.queryset().filter(uuid__in=update_uuids).only(*update_fields)
        context = {'request': request}
        serializer = CourseQuizSerializer(queryset, data=request.data, context=context, many=True)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    @method_decorator(never_cache)
    @transaction.atomic
    def partial_update(self, request, uuid=None, format=None):
        context = {'request': request}
        try:
            queryset = self.queryset().select_for_update().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = CourseQuizSerializer(queryset, data=request.data, partial=True, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)
