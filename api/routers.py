from django.conf import settings
from django.urls import path, include

from apps.person.api import routers as person_routers
from apps.training.api import routers as training_routers

from api.views import RootApiView

_API_VERSION = settings.API_VERSION_SLUG

urlpatterns = [
    path('', RootApiView.as_view(), name='api'),
    path(_API_VERSION + '/person/', include((person_routers, 'person_api'), namespace='person_apis_' + _API_VERSION)),
    path(_API_VERSION + '/training/', include((training_routers, 'training_api'), namespace='training_apis_' + _API_VERSION)),
]
