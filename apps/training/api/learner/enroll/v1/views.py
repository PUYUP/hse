from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from utils.generals import get_model
from utils.pagination import build_result_pagination

from .serializers import EnrollSerializer, SimulationSerializer

Enroll = get_model('training', 'Enroll')
Simulation = get_model('training', 'Simulation')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class EnrollApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def initialize_request(self, request, *args, **kwargs):
        self.user = request.user
        return super().initialize_request(request, *args, **kwargs)

    def queryset(self):
        qs = Enroll.objects \
            .prefetch_related('learner', 'course') \
            .select_related('learner', 'course') \
            .filter(learner_id=self.user.id)

        return qs

    def get_object(self, uuid=None):
        try:
            queryset = self.queryset().get(uuid=uuid)
        except (ObjectDoesNotExist, ValidationError) as e:
            raise NotAcceptable(detail=repr(e))

        return queryset

    def list(self, request, format=None):
        context = {'request': request}
        queryset = self.queryset()
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

        if queryset.learner.uuid != self.user.uuid:
            raise NotAcceptable(detail=_("Restricted!"))

        queryset.delete()
        return Response({'detail': _("Delete success!")},
                        status=response_status.HTTP_204_NO_CONTENT)


class SimulationApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def initialize_request(self, request, *args, **kwargs):
        self.user = request.user
        return super().initialize_request(request, *args, **kwargs)

    def queryset(self):
        qs = Simulation.objects \
            .prefetch_related('learner', 'enroll', 'course') \
            .select_related('learner', 'enroll', 'course') \
            .filter(learner_id=self.user.id)

        return qs

    def get_object(self, uuid=None):
        try:
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
        context = {'request': request}
    
        queryset = self.get_object(uuid=uuid)
    
        serializer = SimulationSerializer(queryset, many=False, context=context)
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
    def destroy(self, request, uuid=None, format=None):
        queryset = self.get_object(uuid=uuid)

        if queryset.learner.uuid != self.user.uuid:
            raise NotAcceptable(detail=_("Restricted!"))

        queryset.delete()
        return Response({'detail': _("Delete success!")},
                        status=response_status.HTTP_204_NO_CONTENT)
