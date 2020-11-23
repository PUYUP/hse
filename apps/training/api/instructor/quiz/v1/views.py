from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from utils.generals import get_model
from .serializers import QuestionSerializer

Question = get_model('training', 'Question')


class QuestionApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def queryset(self):
        query = Question.objects \
            .prefetch_related('choice')
        return query

    def initialize_request(self, request, *args, **kwargs):
        self.position = request.GET.get('position')
        self.course_uuid = request.GET.get('course_uuid')
        self.choice = request.GET.get('choice')
        
        return super().initialize_request(request, *args, **kwargs)

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request, 'position': self.position, 'course_uuid': self.course_uuid}
        serializer = QuestionSerializer(data=request.data, context=context)
        
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
        update_fields = []
        update_uuids = [item.get('uuid') for item in request.data]

        # Collect fields affect for updated
        for item in request.data:
            keys = list(item.keys())
            if 'choice' not in keys:
                update_fields.extend(list(item.keys()))

        update_fields = list(dict.fromkeys(update_fields))
        queryset = self.queryset().filter(uuid__in=update_uuids).only(*update_fields)
        context = {'request': request, 'position': self.position, 'course_uuid': self.course_uuid,
                   'choice': self.choice}
        serializer = QuestionSerializer(queryset, data=request.data, context=context, many=True)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)
