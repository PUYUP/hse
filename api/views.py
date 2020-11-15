# THIRD PARTY
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny


class RootApiView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return Response({
            'person': {
                'token': reverse('person_api:token_obtain_pair', request=request,
                                 format=format, current_app='person_api'),
                'token-refresh': reverse('person_api:token_refresh', request=request,
                                         format=format, current_app='person_api'),
                'users': reverse('person_api:user-list', request=request,
                                 format=format, current_app='person_api'),
                'verifycodes': reverse('person_api:verifycode-list', request=request,
                                format=format, current_app='person_api'),
            },
            'training': {
                'learner': {
                    'courses': reverse('training_api:learner:course-list', request=request,
                                       format=format, current_app='helpdesk_api:client'),
                    'coursequizs': reverse('training_api:learner:coursequiz-list', request=request,
                                            format=format, current_app='helpdesk_api:client'),
                    'enrolls': reverse('training_api:learner:enroll-list', request=request,
                                       format=format, current_app='helpdesk_api:client'),
                    'simulations': reverse('training_api:learner:simulation-list', request=request,
                                           format=format, current_app='helpdesk_api:client'),
                    'quizquestions': reverse('training_api:learner:quizquestion-list', request=request,
                                             format=format, current_app='helpdesk_api:client'),
                    'answers': reverse('training_api:learner:answer-list', request=request,
                                       format=format, current_app='helpdesk_api:client'),
                }
            }
        })
