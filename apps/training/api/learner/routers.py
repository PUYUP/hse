from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .course.v1.views import CourseApiView, CourseQuizApiView
from .enroll.v1.views import EnrollApiView, SimulationApiView
from .quiz.v1.views import QuizQuestionApiView, AnswerApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('courses', CourseApiView, basename='course')
router.register('coursequizs', CourseQuizApiView, basename='coursequiz')
router.register('enrolls', EnrollApiView, basename='enroll')
router.register('simulations', SimulationApiView, basename='simulation')
router.register('quizquestions', QuizQuestionApiView, basename='quizquestion')
router.register('answers', AnswerApiView, basename='answer')

app_name = 'learner'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
