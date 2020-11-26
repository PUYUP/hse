from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from utils.generals import get_model
from .serializers import ChoiceSerializer, QuestionSerializer, QuizQuestionSerializer, QuizSerializer

Question = get_model('training', 'Question')
Choice = get_model('training', 'Choice')
Quiz = get_model('training', 'Quiz')
QuizQuestion = get_model('training', 'QuizQuestion')


class QuestionApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def queryset(self):
        query = Question.objects.prefetch_related('choice')
        return query

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = QuestionSerializer(data=request.data, context=context, many=True)
        
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
            update_fields.extend(list(item.keys()))

        update_fields = list(dict.fromkeys(update_fields))
        queryset = self.queryset().filter(uuid__in=update_uuids).only(*update_fields)

        context = {'request': request}
        serializer = QuestionSerializer(queryset, data=request.data, context=context, many=True)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)


class ChoiceApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def queryset(self):
        query = Choice.objects \
            .prefetch_related('question', 'creator') \
            .select_related('question', 'creator')

        return query

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = ChoiceSerializer(data=request.data, context=context)
        
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
        update_fields = ['creator', 'question']
        update_uuids = [item.get('uuid') for item in request.data]

        # Collect fields affect for updated
        for item in request.data:
            update_fields.extend(list(item.keys()))

        update_fields = list(dict.fromkeys(update_fields))
        queryset = self.queryset().filter(uuid__in=update_uuids).only(*update_fields)
        context = {'request': request}
        serializer = ChoiceSerializer(queryset, data=request.data, context=context, many=True)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)


class QuizApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def queryset(self):
        query = Quiz.objects.all()
        return query

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = QuizSerializer(data=request.data, context=context)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)


class QuizQuestionApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def queryset(self):
        query = QuizQuestion.objects \
            .prefetch_related('question', 'quiz') \
            .select_related('question', 'quiz')

        return query

    def list(self, request, format=None):
        return Response({}, status=response_status.HTTP_200_OK)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = QuizQuestionSerializer(data=request.data, context=context)
        
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
        update_fields = ['quiz', 'question']
        update_uuids = [item.get('uuid') for item in request.data]

        # Collect fields affect for updated
        for item in request.data:
            update_fields.extend(list(item.keys()))

        update_fields = list(dict.fromkeys(update_fields))
        queryset = self.queryset().filter(uuid__in=update_uuids).only(*update_fields)
        context = {'request': request}
        serializer = QuizQuestionSerializer(queryset, data=request.data, context=context, many=True)
        
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                raise NotAcceptable(detail=str(e))

            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)
