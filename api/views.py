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
                                       format=format, current_app='training_api:learner'),
                    'coursequizs': reverse('training_api:learner:coursequiz-list', request=request,
                                            format=format, current_app='training_api:learner'),
                    'enrolls': reverse('training_api:learner:enroll-list', request=request,
                                       format=format, current_app='training_api:learner'),
                    'simulations': reverse('training_api:learner:simulation-list', request=request,
                                           format=format, current_app='training_api:learner'),
                    'simulationchapters': reverse('training_api:learner:simulationchapter-list', request=request,
                                                  format=format, current_app='training_api:learner'),
                    'simulationquizs': reverse('training_api:learner:simulationquiz-list', request=request,
                                               format=format, current_app='training_api:learner'),
                    'quizquestions': reverse('training_api:learner:quizquestion-list', request=request,
                                             format=format, current_app='training_api:learner'),
                    'answers': reverse('training_api:learner:answer-list', request=request,
                                       format=format, current_app='training_api:learner'),
                    'chapters': reverse('training_api:learner:chapter-list', request=request,
                                        format=format, current_app='training_api:learner'),
                    'categories': reverse('training_api:learner:category-list', request=request,
                                          format=format, current_app='training_api:learner'),
                },
                'instructor': {
                    'courses': reverse('training_api:instructor:course-list', request=request,
                                       format=format, current_app='training_api:instructor'),
                    'coursequizs': reverse('training_api:instructor:coursequiz-list', request=request,
                                           format=format, current_app='training_api:instructor'),
                    'chapters': reverse('training_api:instructor:chapter-list', request=request,
                                        format=format, current_app='training_api:instructor'),
                    'questions': reverse('training_api:instructor:question-list', request=request,
                                         format=format, current_app='training_api:instructor'),
                    'choices': reverse('training_api:instructor:choice-list', request=request,
                                       format=format, current_app='training_api:instructor'),
                    'quizs': reverse('training_api:instructor:quiz-list', request=request,
                                     format=format, current_app='training_api:instructor'),
                    'quizquestions': reverse('training_api:instructor:quizquestion-list', request=request,
                                             format=format, current_app='training_api:instructor'),
                }
            }
        })
