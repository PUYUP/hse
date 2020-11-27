from django.urls import path

from .console.index import ConsoleView
from .console.learner import LearnerDetailView, LearnerView
from .console.course import ChapterView, CourseView, CourseEditorView, CourseDetailView, CourseQuizView
from .general import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('console/', ConsoleView.as_view(), name='home'),
    path('console/learner/', LearnerView.as_view(), name='learner'),
    path('console/learner/<uuid:uuid>/', LearnerDetailView.as_view(), name='learner_detail'),
    path('console/course/', CourseView.as_view(), name='course'),
    path('console/course/editor/', CourseEditorView.as_view(), name='course_editor'),
    path('console/course/<uuid:uuid>/', CourseDetailView.as_view(), name='course_detail'),
    path('console/course/<uuid:uuid>/editor/', CourseEditorView.as_view(), name='course_editor'),
    path('console/course/<uuid:uuid>/quiz/', CourseQuizView.as_view(), name='course_quiz'),
    path('console/chapter/<uuid:uuid>/editor/', ChapterView.as_view(), name='chapter_editor'),
]
