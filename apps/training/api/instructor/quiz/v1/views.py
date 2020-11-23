from django.core.exceptions import ValidationError
from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import QuestionSerializer


class QuestionApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def initialize_request(self, request, *args, **kwargs):
        self.position = request.GET.get('position')
        self.course_uuid = request.GET.get('course_uuid')
        
        return super().initialize_request(request, *args, **kwargs)

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

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

    def put(self, request, format=None):
        context = {'request': request, 'position': self.position, 'course_uuid': self.course_uuid}
        serializer = QuestionSerializer(data=request.data, context=context, many=True)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)
