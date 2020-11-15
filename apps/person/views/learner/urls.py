from django.urls import path

from .v1.dashboard import Learner_DashboardView

app_name = 'learner'

urlpatterns = [
    path('', Learner_DashboardView.as_view(), name='dashboard'),
]
