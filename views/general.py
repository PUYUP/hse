from django.views import View
from django.shortcuts import render


class HomeView(View):
    template_name = 'home.html'
    context = {}

    def get(self, request):
        return render(request, self.template_name, self.context)
