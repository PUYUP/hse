from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

_APP_VERSION = settings.APP_VERSION_SLUG

from apps.person.decorators import learner_required


@method_decorator([login_required, learner_required], name='dispatch')
class Learner_DashboardView(View):
    template_name = _APP_VERSION + '/person/learner/dashboard.html'
    context = dict()

    def get(self, request):
        return render(request, self.template_name, self.context)
