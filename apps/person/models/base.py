import uuid

from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from apps.person.utils.constants import LEARNER, INSTRUCTOR, REGISTERED


# Extend User
# https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#substituting-a-custom-user-model
class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta(AbstractUser.Meta):
        app_label = 'person'

    def role_identifier(self):
        role = self.role.all().values_list('identifier', flat=True)
        return role

    @property
    def is_registered(self):
        role = self.role_identifier()
        return REGISTERED in role

    @property
    def is_learner(self):
        role = self.role_identifier()
        return LEARNER in role

    @property
    def is_instructor(self):
        role = self.role_identifier()
        return INSTRUCTOR in role

    @property
    def permalink(self):
        from django.urls import reverse
        return reverse('learner_detail', kwargs={'uuid': self.uuid})
