from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views import View
from django.shortcuts import render

from utils.generals import get_model

SimulationAttachment = get_model('training', 'SimulationAttachment')


class HomeView(View):
    template_name = 'home.html'
    context = {}

    def get(self, request):
        return render(request, self.template_name, self.context)


class CertificateView(View):
    template_name = 'certificate.html'
    context = {}

    def get(self, request, uuid=None):
        cert = None
    
        try:
            cert = SimulationAttachment.objects.get(uuid=uuid, identifier='certificate')
        except ObjectDoesNotExist:
            pass
        except ValidationError:
            pass
        
        self.context['cert'] = cert
        return render(request, self.template_name, self.context)
