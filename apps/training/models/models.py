from utils.generals import is_model_registered

from .quiz import *
from .course import *
from .enroll import *

__all__ = []


# 1
if not is_model_registered('training', 'Question'):
    class Question(AbstractQuestion):
        class Meta(AbstractQuestion.Meta):
            db_table = 'training_question'

    __all__.append('Question')


# 2
if not is_model_registered('training', 'Choice'):
    class Choice(AbstractChoice):
        class Meta(AbstractChoice.Meta):
            db_table = 'training_choice'

    __all__.append('Choice')


# 3
if not is_model_registered('training', 'Quiz'):
    class Quiz(AbstractQuiz):
        class Meta(AbstractQuiz.Meta):
            db_table = 'training_quiz'

    __all__.append('Quiz')


# 4
if not is_model_registered('training', 'QuizQuestion'):
    class QuizQuestion(AbstractQuizQuestion):
        class Meta(AbstractQuizQuestion.Meta):
            db_table = 'training_quiz_question'

    __all__.append('QuizQuestion')


# 5
if not is_model_registered('training', 'Category'):
    class Category(AbstractCategory):
        class Meta(AbstractCategory.Meta):
            db_table = 'training_category'

    __all__.append('Category')


# 6
if not is_model_registered('training', 'Course'):
    class Course(AbstractCourse):
        class Meta(AbstractCourse.Meta):
            db_table = 'training_course'

    __all__.append('Course')


# 7
if not is_model_registered('training', 'CourseDate'):
    class CourseDate(AbstractCourseDate):
        class Meta(AbstractCourseDate.Meta):
            db_table = 'training_course_date'

    __all__.append('CourseDate')


# 8
if not is_model_registered('training', 'Chapter'):
    class Chapter(AbstractChapter):
        class Meta(AbstractChapter.Meta):
            db_table = 'training_chapter'

    __all__.append('Chapter')


# 9
if not is_model_registered('training', 'Material'):
    class Material(AbstractMaterial):
        class Meta(AbstractMaterial.Meta):
            db_table = 'training_material'

    __all__.append('Material')


# 10
if not is_model_registered('training', 'CourseQuiz'):
    class CourseQuiz(AbstractCourseQuiz):
        class Meta(AbstractCourseQuiz.Meta):
            db_table = 'training_course_quiz'

    __all__.append('CourseQuiz')


# 11
if not is_model_registered('training', 'Enroll'):
    class Enroll(AbstractEnroll):
        class Meta(AbstractEnroll.Meta):
            db_table = 'training_enroll'

    __all__.append('Enroll')


# 12
if not is_model_registered('training', 'Simulation'):
    class Simulation(AbstractSimulation):
        class Meta(AbstractSimulation.Meta):
            db_table = 'training_simulation'

    __all__.append('Simulation')


# 13
if not is_model_registered('training', 'SimulationChapter'):
    class SimulationChapter(AbstractSimulationChapter):
        class Meta(AbstractSimulationChapter.Meta):
            db_table = 'training_simulation_chapter'

    __all__.append('SimulationChapter')


# 14
if not is_model_registered('training', 'SimulationQuiz'):
    class SimulationQuiz(AbstractSimulationQuiz):
        class Meta(AbstractSimulationQuiz.Meta):
            db_table = 'training_simulation_quiz'

    __all__.append('SimulationQuiz')


# 15
if not is_model_registered('training', 'Answer'):
    class Answer(AbstractAnswer):
        class Meta(AbstractAnswer.Meta):
            db_table = 'training_answer'

    __all__.append('Answer')


# 16
if not is_model_registered('training', 'Certificate'):
    class Certificate(AbstractCertificate):
        class Meta(AbstractCertificate.Meta):
            db_table = 'training_certificate'

    __all__.append('Certificate')
