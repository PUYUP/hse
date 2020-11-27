from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import query
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser

from utils.generals import get_model
from .serializers import ChapterSerializer

Chapter = get_model('training', 'Chapter')


class ChapterApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)
    parser_classes = (JSONParser, MultiPartParser,)

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = ChapterSerializer(data=request.data, context=context)
        
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
            queryset = Chapter.objects.select_for_update().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = ChapterSerializer(queryset, partial=True, data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)
