import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..utils.constants import BEFORE, POSITION_CHOICES


class AbstractCategory(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='category')

    label = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.label


class AbstractCourse(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='course')
    category = models.ForeignKey('training.Category', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='course')

    label = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    cover = models.ImageField(max_length=500, upload_to='images/course', null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text=_("Available for public or not"))

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.label


class AbstractCourseDate(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='course_date')
    start_date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Course Date")
        verbose_name_plural = _("Course Dates")

    def __str__(self):
        return str(self.start_date)


class AbstractChapter(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='chapter')

    label = models.CharField(max_length=255)
    number = models.CharField(max_length=15, help_text=_("E.g 1"))

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Chapter")
        verbose_name_plural = _("Chapters")

    def __str__(self):
        return self.label


class AbstractMaterial(models.Model):
    MEDIA = 'media'
    TEXT = 'text'
    MATERIAL_TYPES = (
        (MEDIA, _("Media")),
        (TEXT, _("Text")),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='material')
    chapter = models.ForeignKey('training.Chapter', on_delete=models.CASCADE,
                                related_name='material')

    type = models.CharField(choices=MATERIAL_TYPES, default=MEDIA, max_length=10)
    media = models.FileField(max_length=500, upload_to='material/file', null=True, blank=True,
                             help_text=_("Place video, audio, pdf or image here"))
    text = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")

    def __str__(self):
        return self.chapter.label


class AbstractCourseQuiz(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    course = models.ForeignKey('training.Course', on_delete=models.CASCADE,
                               related_name='course_quiz')
    quiz = models.ForeignKey('training.Quiz', on_delete=models.SET_NULL,
                             null=True, related_name='course_quiz')

    position = models.CharField(choices=POSITION_CHOICES, default=BEFORE,
                                max_length=15, help_text=_("Before or after Course"))
    duration = models.IntegerField(default=15, help_text=_("In minutes, set 0 for unlimited"))

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Course Quiz")
        verbose_name_plural = _("Course Quizs")
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'quiz', 'position'], 
                name='unique_course_quiz'
            )
        ]

    def __str__(self):
        return self.quiz.label


class AbstractCertificate(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='certificate')
    course = models.ForeignKey('training.Course', on_delete=models.SET_NULL,
                               null=True, related_name='certificate')
    media = models.FileField(max_length=500, upload_to='certificate')

    class Meta:
        abstract = True
        app_label = 'training'
        ordering = ['-create_date']
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")

    def __str__(self):
        return self.learner.username
