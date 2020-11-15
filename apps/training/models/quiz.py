import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractQuestion(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='question')

    label = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __str__(self):
        return self.label


class AbstractChoice(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='choice')
    question = models.ForeignKey('training.Question', on_delete=models.CASCADE,
                                 related_name='choice')

    label = models.CharField(max_length=255)
    identifier = models.CharField(max_length=1, help_text=_("One of A, B, C or D"))
    description = models.TextField(null=True, blank=True)
    is_true = models.BooleanField(default=False, help_text=_("Mark as true choice?"))

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Choice")
        verbose_name_plural = _("Choices")
        ordering = ['identifier']

    def __str__(self):
        return self.label


class AbstractQuiz(models.Model):
    """
    Grouping Question as Quiz
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)
    
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='quiz')

    label = models.CharField(max_length=255, help_text=_("Ex: Quiz before training [name training]"))

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizs")

    def __str__(self):
        return self.label


class AbstractQuizQuestion(models.Model):
    """
    Add Question to Quiz
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    quiz = models.ForeignKey('training.Quiz', on_delete=models.CASCADE,
                             related_name='quiz_question')
    question = models.ForeignKey('training.Question', on_delete=models.CASCADE,
                                 related_name='quiz_question')

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Quiz Question")
        verbose_name_plural = _("Quiz Questions")

    def __str__(self):
        return self.quiz.label
