from django.urls import path, include

from .learner import routers as learner_routers
from .instructor import routers as instructor_routers

app_name = 'training_api'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('learner/', include(learner_routers)),
    path('instructor/', include(instructor_routers)),
]
