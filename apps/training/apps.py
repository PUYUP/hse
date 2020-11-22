from django.apps import AppConfig
from django.db.models.signals import post_save


class TrainingConfig(AppConfig):
    name = 'apps.training'

    def ready(self):
        from utils.generals import get_model

        from .singals import enroll_session_save_handler

        EnrollSession = get_model('training', 'EnrollSession')

        post_save.connect(enroll_session_save_handler, sender=EnrollSession,
                          dispatch_uid='enroll_session_save_signal')
