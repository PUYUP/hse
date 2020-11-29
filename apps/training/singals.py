from django.db import transaction
from django.utils import timezone

from utils.generals import get_model

Quiz = get_model('training', 'Quiz')
CourseQuiz = get_model('training', 'CourseQuiz')
CourseSession = get_model('training', 'CourseSession')
Simulation = get_model('training', 'Simulation')
SimulationQuiz = get_model('training', 'SimulationQuiz')
SimulationChapter = get_model('training', 'SimulationChapter')


@transaction.atomic
def course_save_handler(sender, instance, created, **kwargs):
    if created:
        course_session = CourseSession.objects \
            .create(course=instance, start_date=timezone.now(),
                    end_date=timezone.now(), max_repeated=0)


@transaction.atomic
def enroll_session_save_handler(sender, instance, created, **kwargs):
    if created:
        """
        Evaluate enroll save
        Create first simulation and first progress as quiz
        """
        enroll = instance.enroll
        learner = enroll.learner
        course = enroll.course
        course_session = instance.course_session

        # First simulation.
        simulation = Simulation.objects.create(learner=learner, course=course, course_session=course_session,
                                               enroll=enroll, enroll_session=instance)

        # Simulation quiz survey
        course_quiz = CourseQuiz.objects.get(course__id=course.id, position='survey')
        SimulationQuiz.objects.create(simulation=simulation, course=course, course_quiz=course_quiz,
                                      quiz=course_quiz.quiz)
