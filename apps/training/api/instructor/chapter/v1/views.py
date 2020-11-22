from django.core.exceptions import ValidationError
from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser

from .serializers import ChapterSerializer


class ChapterApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, MultiPartParser,)

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

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
