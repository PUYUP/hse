import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ..utils.constants import AFTER, BEFORE


class AbstractEnroll(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='enroll')
    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='enroll')
    course_date = models.ForeignKey('training.CourseDate', on_delete=models.CASCADE,
                                    related_name='enroll')

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Enroll")
        verbose_name_plural = _("Enrolls")

    def __str__(self):
        return self.course.label


class AbstractSimulation(models.Model):
    """
    Each enroll has multiple simulation
    This handle for re-try the course
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='simulation')
    enroll = models.ForeignKey('training.Enroll', on_delete=models.CASCADE,
                               related_name='simulation')
    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='simulation')

    repeat_number = models.IntegerField(default=1)
    is_done = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Simulation")
        verbose_name_plural = _("Simulations")

    def __str__(self):
        return self.course.label

    def save(self, *args, **kwargs):
        old_objs = self.__class__.objects.filter(learner=self.learner, enroll=self.enroll,
                                                 course=self.course)

        # Mark old simulation as Done if new simulation created
        old_objs_not_done = old_objs.filter(is_done=False)
        if not self.is_done and old_objs_not_done.exists():
            old_objs_not_done.update(is_done=True)

        if not self.pk:
            self.repeat_number = old_objs.count() + 1

        super().save(*args, **kwargs)


class AbstractSimulationChapter(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    simulation = models.ForeignKey('training.Simulation', on_delete=models.CASCADE,
                                   related_name='simulation_chapter')
    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='simulation_chapter')
    chapter = models.ForeignKey('training.Chapter', on_delete=models.CASCADE,
                                related_name='simulation_chapter')

    is_done = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Simulation Chapter")
        verbose_name_plural = _("Simulation Chapters")

    def __str__(self):
        return self.course_chapter.label


class AbstractSimulationQuiz(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    simulation = models.ForeignKey('training.Simulation', on_delete=models.CASCADE,
                                   related_name='simulation_quiz')
    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='simulation_quiz')
    course_quiz = models.ForeignKey('training.CourseQuiz', on_delete=models.CASCADE,
                                    related_name='simulation_quiz')
    quiz = models.ForeignKey('training.Quiz', on_delete=models.CASCADE,
                             related_name='simulation_quiz')

    is_done = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Simulation Quiz")
        verbose_name_plural = _("Simulation Quizs")
        constraints = [
            models.UniqueConstraint(
                fields=['simulation', 'course', 'course_quiz', 'quiz'], 
                name='unique_simulation_quiz'
            )
        ]

    def __str__(self):
        return self.quiz.label

    @property
    def is_before(self):
        return self.course_quiz.position == BEFORE

    @property
    def is_after(self):
        return self.course_quiz.position == AFTER


class AbstractAnswer(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='answer')
    simulation = models.ForeignKey('training.Simulation', on_delete=models.CASCADE,
                                   related_name='answer')
    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='answer')
    course_quiz = models.ForeignKey('training.CourseQuiz', on_delete=models.CASCADE,
                                    related_name='answer')
    quiz = models.ForeignKey('training.Quiz', on_delete=models.CASCADE,
                             related_name='answer')
    question = models.ForeignKey('training.Question', on_delete=models.CASCADE,
                                 related_name='answer')
    choice = models.ForeignKey('training.Choice', on_delete=models.CASCADE,
                               related_name='answer')

    position = models.CharField(max_length=15, editable=False)
    is_true = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")

    def __str__(self):
        return self.question.label

    def save(self, *args, **kwargs):
        self.position = self.course_quiz.position
        self.is_true = self.choice.is_true

        super().save(*args, **kwargs)
