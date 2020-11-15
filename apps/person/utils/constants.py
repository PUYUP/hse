from dateutil import rrule
from django.utils.translation import ugettext_lazy as _


REGISTERED = 'registered'
LEARNER = 'learner'
INSTRUCTOR = 'instructor'
ROLE_IDENTIFIERS = (
    (REGISTERED, _(u"Registered")),
    (LEARNER, _(u"Learner")),
    (INSTRUCTOR, _(u"Instructor")),
)

ROLE_DEFAULTS = (
    (REGISTERED, _(u"Registered")),
)

ROLE_ALLOWED = (
    (LEARNER, _(u"Learner")),
    (INSTRUCTOR, _(u"Instructor")),
)


VerifyCode_SESSION_FIELDS = ['uuid', 'token', 'challenge', 'msisdn', 'email', 'info']
EMAIL_VALIDATION = 'email_validation'
MSISDN_VALIDATION = 'msisdn_validation'
REGISTER_VALIDATION = 'register_validation'
PASSWORD_RECOVERY = 'password_recovery'
CHANGE_MSISDN = 'change_msisdn'
CHANGE_EMAIL = 'change_email'
CHANGE_USERNAME = 'change_username'
CHANGE_PASSWORD = 'change_password'
VerifyCode_CHALLENGE = (
    (EMAIL_VALIDATION, _(u"Email Validation")),
    (MSISDN_VALIDATION, _(u"MSISDN Validation")),
    (REGISTER_VALIDATION, _(u"Register Validation")),
    (PASSWORD_RECOVERY, _(u"Password Recovery")),
    (CHANGE_MSISDN, _(u"Change MSISDN")),
    (CHANGE_EMAIL, _(u"Change Email")),
    (CHANGE_USERNAME, _(u"Change Username")),
    (CHANGE_PASSWORD, _(u"Change Password")),
)


UNDEFINED = 'unknown'
MALE = 'male'
FEMALE = 'female'
GENDER_CHOICES = (
    (UNDEFINED, _(u"Unknown")),
    (MALE, _(u"Male")),
    (FEMALE, _(u"Female")),
)


setattr(rrule, 'FD', 'FD')
RRULE_WKST_CHOICES = (
    (str(rrule.MO), _(u"Monday")),
    (str(rrule.TU), _(u"Tuesday")),
    (str(rrule.WE), _(u"Wednesday")),
    (str(rrule.TH), _(u"Thursday")),
    (str(rrule.FR), _(u"Friday")),
    (str(rrule.SA), _(u"Saturday")),
    (str(rrule.SU), _(u"Sunday")),
    (str(rrule.FD), _(u"Few days")),
)
