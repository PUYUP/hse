from django.views import View
from django.shortcuts import render


class HomeView(View):
    template_name = 'console/home.html'
    context = {}

    def get(self, request):
        return render(self.request, self.template_name, self.context)
