from django.urls import path

from .console.home import HomeView
from .console.learner import LearnerView
from .console.course import CourseView, CourseEditorView, CourseDetailView, CourseQuizView

urlpatterns = [
    path('console/', HomeView.as_view(), name='home'),
    path('console/learner/', LearnerView.as_view(), name='learner'),
    path('console/course/', CourseView.as_view(), name='course'),
    path('console/course/editor/', CourseEditorView.as_view(), name='course_editor'),
    path('console/course/<uuid:uuid>/', CourseDetailView.as_view(), name='course_detail'),
    path('console/course/<uuid:uuid>/editor/', CourseEditorView.as_view(), name='course_editor'),
    path('console/course/<uuid:uuid>/quiz/', CourseQuizView.as_view(), name='course_quiz'),
]
