from django.urls import path

from .console.index import ConsoleView
from .console.learner import LearnerDetailView, LearnerView
from .console.course import ChapterView, CourseView, CourseEditorView, CourseDetailView, CourseQuizView
from .general import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', ConsoleView.as_view(), name='home'),
    path('dashboard/learner/', LearnerView.as_view(), name='learner'),
    path('dashboard/learner/<uuid:uuid>/', LearnerDetailView.as_view(), name='learner_detail'),
    path('dashboard/course/', CourseView.as_view(), name='course'),
    path('dashboard/course/editor/', CourseEditorView.as_view(), name='course_editor'),
    path('dashboard/course/<uuid:uuid>/', CourseDetailView.as_view(), name='course_detail'),
    path('dashboard/course/<uuid:uuid>/editor/', CourseEditorView.as_view(), name='course_editor'),
    path('dashboard/course/<uuid:uuid>/quiz/', CourseQuizView.as_view(), name='course_quiz'),
    path('dashboard/chapter/<uuid:uuid>/editor/', ChapterView.as_view(), name='chapter_editor'),
]
