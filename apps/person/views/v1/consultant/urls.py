from django.urls import path

from .dashboard import Instructor_DashboardView

app_name = 'instructor'

urlpatterns = [
    path('', Instructor_DashboardView.as_view(), name='dashboard'),
]
