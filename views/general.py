from django.views import View
from django.shortcuts import render


class HomeView(View):
    template_name = 'home.html'
    context = {}

    def get(self, request):
        return render(request, self.template_name, self.context)


class CertificateView(View):
    template_name = 'certificate.html'
    conteext = {}

    def get(self, request, uuid=None):
        return render(request, self.template_name, self.context)
