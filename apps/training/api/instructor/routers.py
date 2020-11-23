from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .course.v1.views import CourseApiView
from .chapter.v1.views import ChapterApiView
from .quiz.v1.views import QuestionApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('courses', CourseApiView, basename='course')
router.register('chapters', ChapterApiView, basename='chapter')
router.register('questions', QuestionApiView, basename='question')

app_name = 'instructor'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
