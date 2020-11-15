from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model

Quiz = get_model('training', 'Quiz')
CourseQuiz = get_model('training', 'CourseQuiz')
Simulation = get_model('training', 'Simulation')
SimulationQuiz = get_model('training', 'SimulationQuiz')
SimulationChapter = get_model('training', 'SimulationChapter')


@transaction.atomic
def enroll_save_handler(sender, instance, created, **kwargs):
    if created:
        """
        After enroll save
        Create first simulation and first progress as quiz
        """
        learner = instance.learner
        course = instance.course

        # First simulation.
        simulation = Simulation.objects.create(learner=learner, course=course, enroll=instance)

        # Simulation quiz before
        course_quiz = CourseQuiz.objects.get(course__id=course.id, position='before')
        SimulationQuiz.objects.create(simulation=simulation, course=course, course_quiz=course_quiz,
                                      quiz=course_quiz.quiz)
