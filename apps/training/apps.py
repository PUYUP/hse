from django.apps import AppConfig
from django.db.models.signals import post_save


class TrainingConfig(AppConfig):
    name = 'apps.training'

    def ready(self):
        from utils.generals import get_model

        from .singals import enroll_save_handler

        Enroll = get_model('training', 'Enroll')

        post_save.connect(enroll_save_handler, sender=Enroll,
                          dispatch_uid='enroll_save_signal')
