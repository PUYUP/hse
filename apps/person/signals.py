from django.db import transaction, IntegrityError
from django.db.models import Q, Case, When, Value

from utils.generals import get_model
from apps.person.utils.constants import ROLE_DEFAULTS
from apps.person.utils.auth import set_role

# Celery task
from apps.person.tasks import send_verifycode_email

Account = get_model('person', 'Account')
Profile = get_model('person', 'Profile')
Role = get_model('person', 'Role')


@transaction.atomic
def user_save_handler(sender, instance, created, **kwargs):
    if created:
        account = getattr(instance, 'account', None)
        if account is None:
            try:
                Account.objects.create(user=instance, email=instance.email,
                                       email_verified=True)
            except IntegrityError:
                pass

        profile = getattr(instance, 'profile', None)
        if profile is None:
            try:
                Profile.objects.create(user=instance)
            except IntegrityError:
                pass

        # Set role if created by admin
        role = getattr(instance, 'role_input', None)
        if role is None:
            # Create role on register
            Role.objects.create(user=instance)

            # set default role
            role = list()
            for item in ROLE_DEFAULTS:
                role.append(item[0])
        set_role(user=instance, role=role)

    if not created:
        # create Account if not exist
        if not hasattr(instance, 'account'):
            Account.objects.create(user=instance, email=instance.email,
                                   email_verified=False)
        else:
            instance.account.email = instance.email
            instance.account.save()

        # create Profile if not exist
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)


@transaction.atomic
def verifycodecode_save_handler(sender, instance, created, **kwargs):
    # create tasks
    # run only on resend and created
    if instance.is_used == False and instance.is_verified == False:
        if instance.email:
            data = {
                'email': getattr(instance, 'email', None),
                'passcode': getattr(instance, 'passcode', None)
            }
            # send_verifycode_email.delay(data)
            send_verifycode_email(data)

        # mark older VerifyCode Code to expired
        oldest = instance.__class__.objects \
            .filter(
                Q(challenge=instance.challenge),
                Q(is_used=False), Q(is_expired=False),
                Q(email=Case(When(email__isnull=False, then=Value(instance.email))))
                | Q(msisdn=Case(When(msisdn__isnull=False, then=Value(instance.msisdn))))
            ).exclude(passcode=instance.passcode)

        if oldest.exists():
            oldest.update(is_expired=True)
