from django.urls import path, include
from django.contrib.auth import views as auth_views

from .instructor import urls as instructor_urls
from .learner import urls as learner_urls
from .v1.user import ProfileView, SecurityView, UserDetailView
from .v1.auth import (
    LoginPasswordView, LostPasswordRecoveryView, RegisterCaptureView,
    RegisterView, LoginView, LostPasswordView, VerifyCodeView
)

app_name = 'person_view'

urlpatterns = [
    # BOTH INSTRUCTOR and LEARNER USED THIS
    path('login/', LoginView.as_view(), name='login'),
    path('login/password/', LoginPasswordView.as_view(), name='login_password'),
    path('verifycode-validation/', VerifyCodeView.as_view(), name='verifycode_validate'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('lost-password/', LostPasswordView.as_view(), name='lost_password'),
    path('lost-password/recovery/', LostPasswordRecoveryView.as_view(), name='lost_password_recovery'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/capture/', RegisterCaptureView.as_view(), name='register_capture'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('security/', SecurityView.as_view(), name='security'),
    path('<uuid:uuid>/', UserDetailView.as_view(), name='user_detail'),

    # INSTRUCTOR URL's
    path('instructor/', include(instructor_urls, namespace='instructor')),

    # LEARNER URL's
    path('learner/', include(learner_urls, namespace='learner')),
]
