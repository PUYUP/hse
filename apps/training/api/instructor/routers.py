from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .course.v1.views import CourseApiView, CourseQuizApiView
from .chapter.v1.views import ChapterApiView
from .quiz.v1.views import QuestionApiView, ChoiceApiView, QuizApiView, QuizQuestionApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('courses', CourseApiView, basename='course')
router.register('coursequizs', CourseQuizApiView, basename='coursequiz')
router.register('chapters', ChapterApiView, basename='chapter')
router.register('questions', QuestionApiView, basename='question')
router.register('choices', ChoiceApiView, basename='choice')
router.register('quizs', QuizApiView, basename='quiz')
router.register('quizquestions', QuizQuestionApiView, basename='quizquestion')

app_name = 'instructor'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
