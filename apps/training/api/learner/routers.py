from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .course.v1.views import ChapterApiView, CourseApiView, CourseQuizApiView
from .enroll.v1.views import EnrollApiView, SimulationApiView, SimulationQuizApiView, SimulationChapterApiView
from .quiz.v1.views import QuizQuestionApiView, AnswerApiView
from .master.views import CategoryApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('courses', CourseApiView, basename='course')
router.register('coursequizs', CourseQuizApiView, basename='coursequiz')
router.register('enrolls', EnrollApiView, basename='enroll')
router.register('simulations', SimulationApiView, basename='simulation')
router.register('simulationchapters', SimulationChapterApiView, basename='simulationchapter')
router.register('simulationquizs', SimulationQuizApiView, basename='simulationquiz')
router.register('quizquestions', QuizQuestionApiView, basename='quizquestion')
router.register('answers', AnswerApiView, basename='answer')
router.register('chapters', ChapterApiView, basename='chapter')
router.register('categories', CategoryApiView, basename='category')

app_name = 'learner'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
