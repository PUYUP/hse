from django.urls import path

from .dashboard import Learner_DashboardView

app_name = 'learner'

urlpatterns = [
    path('', Learner_DashboardView.as_view(), name='dashboard'),
]
