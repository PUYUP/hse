from django.conf import settings
from apps.person.utils.constants import LEARNER, INSTRUCTOR


"""Define global attributes for templates"""
def extend(request):
    params = {
        'url_name': request.resolver_match.url_name,
        'app_name': settings.APP_NAME,
        'api_version': settings.API_VERSION_SLUG,
        'app_version': settings.APP_VERSION_SLUG,
        'role_learner': LEARNER,
        'role_instructor': INSTRUCTOR,
    }

    return params
