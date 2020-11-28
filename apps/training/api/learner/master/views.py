from rest_framework import viewsets, status as response_status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.generals import get_model
from .serializers import CategorySerializer

Category = get_model('training', 'Category')


class CategoryApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def list(self, request, format=None):
        context = {'request': request}
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
