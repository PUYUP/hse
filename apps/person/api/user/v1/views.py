from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch, Q, F, Case, When, Value, Count, Subquery, OuterRef, Case, When
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
    MultipleObjectsReturned
)
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# THIRD PARTY
from rest_framework import status as response_status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import JSONParser, MultiPartParser

# JWT
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

# SERIALIZERS 
from .serializers import UserSerializer, AccountSerializer
from ...profile.v1.serializers import ProfileSerializer

# GET MODELS FROM GLOBAL UTILS
from utils.generals import get_model
from utils.pagination import build_result_pagination
from apps.person.utils.permissions import IsCurrentUserOrReject
from apps.person.utils.auth import validate_username
from apps.person.utils.constants import PASSWORD_RECOVERY

User = get_model('person', 'User')
Account = get_model('person', 'Account')
Profile = get_model('person', 'Profile')
VerifyCode = get_model('person', 'VerifyCode')

Simulation = get_model('training', 'Simulation')
Quiz = get_model('training', 'Quiz')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class UserApiView(viewsets.ViewSet):
    """
    POST
    ------------
        If :email provided :msisdn not required
        If :email NOT provide :msisdn required

        {
            "role": [
                {"identifier": "student"}
            ],
            "password": "string with special character",
            "username": "string",
            "email": "string email",
            "msisdn": "string number",
            "token": "string token from verifycode",
            "challenge": "string token caused by, eg: register_validation"
        }
    """
    verifycode_email = None
    verifycode_msisdn = None
    verifycode_token = None

    # this part of DRF
    lookup_field = 'uuid'
    permission_classes = (AllowAny,)
    permission_action = {
        'list': [IsAuthenticated, IsAdminUser],
        'retrieve': [IsAuthenticated, IsCurrentUserOrReject],
        'partial_update': [IsAuthenticated, IsCurrentUserOrReject],
    }

    def get_permissions(self):
        """
        Instantiates and returns
        the list of permissions that this view requires.
        """
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_action
                    [self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def initialize_request(self, request, *args, **kwargs):
        self.uuid = kwargs.get('uuid', None)
        return super().initialize_request(request, *args, **kwargs)

    # Get a object
    def get_object(self, is_update=False):
        queryset = User.objects.all()

        try:
            if is_update:
                queryset = queryset.select_for_update().get(uuid=self.uuid)
            else:
                queryset = queryset.get(uuid=self.uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        return queryset

    # Many objects
    def get_objects(self):
        quiz = Quiz.objects \
            .filter(simulation_quiz__simulation__uuid=OuterRef('uuid')) \
            .annotate(
                true_answer_survey=Count(
                    'simulation_quiz__answer',
                    distinct=True,
                    filter=Q(simulation_quiz__answer__is_true=True, simulation_quiz__answer__course_quiz__position='survey')
                ),
                true_answer_evaluate=Count(
                    'simulation_quiz__answer',
                    distinct=True,
                    filter=Q(simulation_quiz__answer__is_true=True, simulation_quiz__answer__course_quiz__position='evaluate')
                ),
                total_survey_question=Count('quiz_question', distinct=True),
                total_evaluate_question=Count('quiz_question', distinct=True)
            )

        simulation = Simulation.objects \
            .annotate(
                quiz_survey_true_answer=Subquery(quiz.filter(course_quiz__position='survey').values('true_answer_survey')[:1]),
                quiz_evaluate_true_answer=Subquery(quiz.filter(course_quiz__position='evaluate').values('true_answer_evaluate')[:1]),
                total_survey_question=Subquery(quiz.filter(course_quiz__position='survey').values('total_survey_question')[:1]),
                total_evaluate_question=Subquery(quiz.filter(course_quiz__position='evaluate').values('total_evaluate_question')[:1])
            ) \
            .filter(learner__uuid=OuterRef('uuid')) \
            .order_by('-quiz_survey_true_answer', '-quiz_evaluate_true_answer')

        queryset = User.objects.prefetch_related(Prefetch('account'), Prefetch('profile'),
                                                 Prefetch('simulation')) \
            .select_related('account', 'profile') \
            .annotate(
                simulation_count=Count('simulation', distinct=True),
                quiz_survey_true_answer=Coalesce(Subquery(simulation.values('quiz_survey_true_answer')[:1]), 0),
                quiz_evaluate_true_answer=Coalesce(Subquery(simulation.values('quiz_evaluate_true_answer')[:1]), 0),
                total_survey_question=Coalesce(Subquery(simulation.values('total_survey_question')[:1]), 0),
                total_evaluate_question=Coalesce(Subquery(simulation.values('total_evaluate_question')[:1]), 0),
                survey_score=Case(
                    When(Q(total_survey_question__gt=0), then=100/F('total_survey_question') * F('quiz_survey_true_answer')),
                    output_field=IntegerField()
                ),
                evaluate_score=Case(
                    When(Q(total_evaluate_question__gt=0), then=100/F('total_evaluate_question') * F('quiz_evaluate_true_answer')),
                    output_field=IntegerField()
                )
            )

        return queryset

    # All Users
    def list(self, request, format=None):
        context = {'request': self.request}
        role = request.query_params.get('role')
        keyword = request.query_params.get('keyword')
        sort_column = request.query_params.get('sort_column')
        sort_dir = request.query_params.get('sort_dir')
        queryset = self.get_objects()

        if role:
            queryset = queryset.filter(role__identifier__in=[role])

        if keyword:
            queryset = queryset.filter(Q(username__icontains=keyword)
                                       | Q(first_name__icontains=keyword)
                                       | Q(email__icontains=keyword)
                                       | Q(profile__birthdate__icontains=keyword)
                                       | Q(profile__company__icontains=keyword)
                                       | Q(profile__position__icontains=keyword)
                                       | Q(survey_score__icontains=keyword)
                                       | Q(evaluate_score__icontains=keyword))
        
        sort = None
        sort_dir_alias = None
        if sort_dir == 'desc':
            sort_dir_alias = '-'

        # by id
        if sort_column == '0':
            sort = 'id'
            if sort_dir_alias:
                sort = '-id'

        # by first_name
        if sort_column == '1':
            sort = 'first_name'
            if sort_dir_alias:
                sort = '-first_name'

        # by email
        if sort_column == '2':
            sort = 'email'
            if sort_dir_alias:
                sort = '-email'
    
        # by birtdate
        if sort_column == '3':
            sort = 'profile__birtdate'
            if sort_dir_alias:
                sort = '-profile__birtdate'

        # by msisdn
        if sort_column == '4':
            sort = 'account__msisdn'
            if sort_dir_alias:
                sort = '-account__msisdn'

        # by company
        if sort_column == '5':
            sort = 'profile__company'
            if sort_dir_alias:
                sort = '-profile__company'

        # by position
        if sort_column == '6':
            sort = 'profile__position'
            if sort_dir_alias:
                sort = '-profile__position'

        # by survey quiz
        if sort_column == '7':
            sort = 'survey_score'
            if sort_dir_alias:
                sort = '-survey_score'

        # by evaluate quiz
        if sort_column == '8':
            sort = 'evaluate_score'
            if sort_dir_alias:
                sort = '-evaluate_score'

        if sort:
            queryset = queryset.order_by(sort)

        queryset_paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = UserSerializer(queryset_paginator, many=True, context=context,
                                    fields_used=('id', 'uuid', 'username', 'url', 'profile', 'account', 'email',
                                                 'permalink', 'simulation_count', 'quiz_survey_true_answer',
                                                 'quiz_evaluate_true_answer', 'total_survey_question',
                                                 'total_evaluate_question', 'survey_score', 'evaluate_score',))
        pagination_result = build_result_pagination(self, _PAGINATOR, serializer)
        return Response(pagination_result, status=response_status.HTTP_200_OK)

    # Single User
    def retrieve(self, request, uuid=None, format=None):
        context = {'request': self.request}
        queryset = self.get_object()

        # limit when other user see the user
        fields_used = ('__all__')
        if str(request.user.uuid) != uuid:
            fields_used = ('uuid', 'username', 'url', 'profile', 'first_name',)

        serializer = UserSerializer(queryset, many=False, context=context, fields_used=fields_used)
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    # Get verifycode object
    def get_verifycode(self, challenge=None):
        try:
            obj = VerifyCode.objects.select_for_update() \
                .get_verified_unused(email=self.verifycode_email, msisdn=self.verifycode_msisdn,
                                     token=self.verifycode_token, challenge=challenge)
            return obj
        except ObjectDoesNotExist:
            raise NotFound(detail=_(u"Kode verifikasi tidak ditemukan"))

    # Register User
    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': self.request}
        serializer = UserSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except ValidationError as e:
                return Response({'detail': e.message}, status=response_status.HTTP_406_NOT_ACCEPTABLE)
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    # Update basic user data
    @method_decorator(never_cache)
    @transaction.atomic
    def partial_update(self, request, uuid=None, format=None):
        context = {'request': self.request}

        # Single object
        instance = self.get_object(is_update=True)

        serializer = UserSerializer(instance, data=request.data, partial=True, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    # Sub-action check email available
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-email', url_name='check-email')
    def check_email(self, request):
        """
        POST
        ------------------

        Param:

            {
                "email": "my@email.com"
            }
        """
        data = request.data
        email = data.get('email', None)
        if not email:
            raise NotFound(_(u"Email not provided"))

        # check format email valid or not
        try:
            validate_email(email)
        except ValidationError as e:
            raise NotAcceptable(detail=_(u" ".join(e.messages)))

        try:
            Account.objects.get(Q(user__account__email=Case(When(user__account__email__isnull=False, then=Value(email))))
                                | Q(email=Case(When(email__isnull=False, then=Value(email)))),
                                email_verified=True)

            raise NotAcceptable(_(u"Email `{email}` sudah terdaftar."
                                  " Jika ini milik Anda hubungi kami.".format(email=email)))
        except MultipleObjectsReturned:
            raise NotAcceptable(_(u"Email `{email}` terdaftar lebih dari satu akun. Jika merasa belum pernah mendaftar"
                                  " dengan email tersebut silahkan hubungi kami.".format(email=email)))
        except ObjectDoesNotExist:
            # Check the email has been used in VerifyCode
            check = VerifyCode.objects.filter(email=email, is_used=False, is_expired=False)
            return Response(
                {
                    'detail': _(u"Email tersedia!"), 
                    'is_used_before': check.exists(), # if True indicate email has used before
                    'is_available': True,
                    'email': email
                },       
                status=response_status.HTTP_200_OK
            )

    # Sub-action check msisdn available
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-msisdn', url_name='check-msisdn')
    def check_msisdn(self, request):
        """
        POST
        ------------------

        Param:

            {
                "msisdn": "1234567890"
            }
        """
        data = request.data
        msisdn = data.get('msisdn', None)
        if not msisdn:
            raise NotFound(_(u"Masukkan MSISDN"))

        try:
            Account.objects.get(msisdn=msisdn, msisdn_verified=True)
            raise NotAcceptable(_(u"MSISDN `{msisdn}` sudah digunakan."
                                  " Jika ini milik Anda hubungi kami.".format(msisdn=msisdn)))
        except MultipleObjectsReturned:
            raise NotAcceptable(_(u"MSISDN `{msisdn}` terdaftar lebih dari satu akun. Jika merasa belum pernah mendaftar"
                                  " dengan msisdn tersebut silahkan hubungi kami.".format(msisdn=msisdn)))
        except ObjectDoesNotExist:
            # Check whether the msisdn has been used
            check = VerifyCode.objects.filter(msisdn=msisdn, is_used=False, is_expired=False)
            return Response(
                {
                    'detail': _(u"MSISDN tersedia!"), 
                    'is_used_before': check.exists(), 
                    'is_available': True,
                    'msisdn': msisdn
                },
                status=response_status.HTTP_200_OK
            )

    # Sub-action check account available
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-account', url_name='check-account')
    def check_account(self, request):
        """
        POST
        ------------------

        Param:

            {
                "account": "my@email.com / username / msisdn"
            }
        """
        data = request.data
        account = data.get('account', None)

        if not account:
            raise NotFound(_(u"Masukkan email, nama pengguna atau MSISDN"))

        try:
            user = User.objects.get(Q(username=account)
                                    | Q(email=account) & Q(account__email_verified=True)
                                    | Q(account__msisdn=account) & Q(account__msisdn_verified=True))

            return Response(
                {
                    'detail': _(u"Akun ditemukan"), 
                    'email': user.email if user.email == account else None, 
                    'msisdn': user.account.msisdn if user.account.msisdn == account else None
                },
                status=response_status.HTTP_200_OK
            )

        except MultipleObjectsReturned:
            raise NotAcceptable(
                {'detail': _(u"Akun `{account}` sudah digunakan".format(account=account))}
            )

        except ObjectDoesNotExist:
            raise NotFound(
                {'detail': _(u"Akun `{account}` tidak ditemukan".format(account=account))}
            )

    # Sub-action check User
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-user', url_name='check-user')
    def check_user(self, request):
        """
        POST
        ------------------

        Param:

            {
                "first_name": "string",
                "msisdn": "string",
                "email": "string",
                "birthplace": "string",
                "birthdate": "yyyy-mm-dd",
            }
        """
        data = request.data
        first_name = data.get('first_name', None)
        msisdn = data.get('msisdn', None)
        email = data.get('email', None)
        birthplace = data.get('birthplace', None)
        birthdate = data.get('birthdate', None)

        try:
            user = User.objects.get(first_name=first_name, email=email, account__msisdn=msisdn,
                                    profile__birthplace=birthplace, profile__birthdate=birthdate)
            return Response({'uuid': user.uuid}, status=response_status.HTTP_200_OK)
        except ValidationError as e:
            raise NotAcceptable(detail=repr(e))
        except ObjectDoesNotExist:
            raise NotFound({'detail': _(u"User tidak ditemukan")})

    # Sub-action check email available
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-username', url_name='check-username')
    def check_username(self, request):
        """
        POST
        ------------------

        Param:

            {
                "username": "string"
            }
        """
        data = request.data
        username = data.get('username', None)
        if not username:
            raise NotFound(_(u"Masukkan nama pengguna"))
        
        # check a username is valid string
        try:
            validate_username(username)
        except ValidationError as e:
            raise NotAcceptable(detail=_(" ".join(e.messages)))

        if User.objects.filter(username=username).exists():
            raise NotAcceptable(detail=_(u"Nama pengguna `{username}` "
                                         "sudah digunakan.".format(username=username)))
        return Response({'detail': _(u"Nama pengguna tersedia!")},
                        status=response_status.HTTP_200_OK)

    # Sub-action update Profile
    # Parses classes must provided because we used this to save JSON and Multipart (upload file)
    @method_decorator(never_cache)
    @transaction.atomic
    @action(detail=True, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated, IsCurrentUserOrReject],
            parser_classes=[JSONParser, MultiPartParser],
            url_path='profile', url_name='profile')
    def profile(self, request, uuid=None):
        context = {'request': self.request}
        try:
            queryset = Profile.objects.get(user__uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        if request.method == 'PATCH':
            serializer = ProfileSerializer(queryset, data=request.data,
                                           partial=True, context=context)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=response_status.HTTP_200_OK)

        if request.method == 'GET':
            serializer = ProfileSerializer(queryset, many=False, context=context)
            return Response(serializer.data, status=response_status.HTTP_200_OK)

    # Sub-action update Account
    # This account need verification
    @method_decorator(never_cache)
    @transaction.atomic
    @action(detail=True, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated, IsCurrentUserOrReject],
            url_path='account', url_name='account')
    def account(self, request, uuid=None):
        """
        POST
        ------------------

        Param;

            {
                "msisdn": "0144151511"
            }
        """
        context = {'request': self.request}
        try:
            queryset = Account.objects.get(user__uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        if request.method == 'PATCH':
            serializer = AccountSerializer(queryset, data=request.data,
                                           partial=True, context=context)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=response_status.HTTP_200_OK)

        if request.method == 'GET':
            serializer = AccountSerializer(queryset, many=False, context=context)
            return Response(serializer.data, status=response_status.HTTP_200_OK)

    # Password recovery as guest
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='password-recovery', url_name='password-recovery')
    def password_recovery(self, request):
        """
        POST
        ------------------

        Param:

            {
                "token": "string",
                "password1": "string",
                "password2": "string",
                "recovery_token": "string",
                "recovery_uidb64": "string"
            }
        
        :token captured from verifycode validation
        """
        self.verifycode_token = request.data.get('token')

        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        recovery_uidb64 = request.data.get('recovery_uidb64')
        recovery_token = request.data.get('recovery_token')

        if not password1 or not password2 or not recovery_uidb64 or not recovery_token:
            raise NotAcceptable(detail=_(u"Parameter tidak lengkap"))

        # check password confirmation
        if password1 and password2:
            if password1 != password2:
                raise NotAcceptable(detail=_(u"Kata sandi tidak sama"))
        else:
            raise NotAcceptable(detail=_(u"Kata sandi tidak boleh kosong"))

        # validate password
        try:
            validate_password(password2)
        except ValidationError as e:
            raise NotAcceptable(detail=' '.join(e.messages))

        # check password recovery valid or not
        uid = urlsafe_base64_decode(recovery_uidb64).decode()
        try:
            user = User._default_manager.get(pk=uid)
            self.verifycode_email = user.email
            self.verifycode_msisdn = user.account.msisdn
        except ObjectDoesNotExist:
            raise NotAcceptable(detail=_(u"Akun tidak ditemukan"))

        isvalid = default_token_generator.check_token(user, recovery_token)
        if not isvalid:
            raise NotAcceptable(detail=_(u"Token invalid"))

        # Get verifycode
        self.verifycode_obj = self.get_verifycode(challenge=PASSWORD_RECOVERY)

        # mark verifycode used
        self.verifycode_obj.mark_used()

        # set password
        user.set_password(password2)
        user.save()

        return Response({'detail': _(u"Kata sandi berhasil diperbarui. "
                                     "Silahkan masuk dengan kata sandi baru")},
                        status=response_status.HTTP_200_OK)

    # Password recovery as guest
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='password-recovery-partial', url_name='password-recovery-partial')
    def password_recovery_partial(self, request):
        """
        POST
        ------------------

        Param:

            {
                "password1": "string",
                "password2": "string",
                "first_name": "string",
                "msisdn": "string",
                "email": "string",
                "birthplace": "string",
                "birthdate": "yyyy-mm-dd"
            }
        """
        user = None
        data = request.data
        password1 = data.get('password1')
        password2 = data.get('password2')
        first_name = data.get('first_name', None)
        msisdn = data.get('msisdn', None)
        email = data.get('email', None)
        birthplace = data.get('birthplace', None)
        birthdate = data.get('birthdate', None)

        # check password confirmation
        if password1 and password2:
            if password1 != password2:
                raise NotAcceptable(detail=_(u"Kata sandi tidak sama"))
        else:
            raise NotAcceptable(detail=_(u"Kata sandi tidak boleh kosong"))

        # validate password
        try:
            validate_password(password2)
        except ValidationError as e:
            raise NotAcceptable(detail=' '.join(e.messages))

        try:
            user = User.objects.get(first_name=first_name, email=email, account__msisdn=msisdn,
                                    profile__birthplace=birthplace, profile__birthdate=birthdate)
        except ValidationError as e:
            raise NotAcceptable(detail=repr(e))
        except ObjectDoesNotExist:
            raise NotFound({'detail': _(u"User tidak ditemukan")})

        # set password
        user.set_password(password2)
        user.save()

        return Response({'detail': _(u"PIN berhasil diperbarui. "
                                     "Silahkan masuk dengan PIN baru")},
                        status=response_status.HTTP_200_OK)

    # Sub-action logout!
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsCurrentUserOrReject],
            url_path='logout', url_name='logout')
    def logout(self, request, uuid=None):
        logout(request)
        return Response({'detail': _(u"Logout!")}, status=response_status.HTTP_204_NO_CONTENT)


class TokenObtainPairSerializerExtend(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user:
            request = self.context.get('request')
            picture = self.user.profile.picture
            picture_url = None
            if picture:
                picture_url = request.build_absolute_uri(picture.url)

            data['uuid'] = self.user.uuid
            data['username'] = self.user.username
            data['first_name'] = self.user.first_name
            data['email'] = self.user.email
            data['msisdn'] = self.user.account.msisdn
            data['picture'] = picture_url
            data['role'] = self.user.role_identifier()
        return data


class TokenObtainPairViewExtend(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerExtend

    @method_decorator(never_cache)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Make user logged-in
        if settings.LOGIN_WITH_JWT:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
        return Response(serializer.validated_data, status=response_status.HTTP_200_OK)
