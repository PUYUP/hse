from django.views import View
from django.shortcuts import render


class ConsoleView(View):
    template_name = 'console/index.html'
    context = {}

    def get(self, request):
        return render(self.request, self.template_name, self.context)
