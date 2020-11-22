from django.db import utils
from django.views import View
from django.shortcuts import render

from utils.generals import get_model

User = get_model('person', 'User')


class LearnerView(View):
    template_name = 'console/learner.html'
    context = {}

    def get(self, request):
        users = User.objects.prefetch_related('account', 'profile') \
            .select_related('account', 'profile') \
            .filter(is_staff=False)
        
        self.context['users'] = users
        return render(self.request, self.template_name, self.context)
