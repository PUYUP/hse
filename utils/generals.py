import uuid
import json
import random
import string
import importlib
import qrcode

from django.conf import settings
from django.apps import apps
from django.apps.config import MODELS_MODULE_NAME
from django.core.exceptions import AppRegistryNotReady
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.utils.text import slugify

from rest_framework import renderers
from PIL import Image, ImageFont, ImageDraw


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class JSONExtendRenderer(renderers.BaseRenderer):
    media_type = 'application/json'
    format = 'json'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)


def is_model_registered(app_label, model_name):
    """
    Checks whether a given model is registered. This is used to only
    register Oscar models if they aren't overridden by a forked app.
    """
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True


def get_model(app_label, model_name):
    """
    Fetches a Django model using the app registry.

    This doesn't require that an app with the given app label exists,
    which makes it safe to call when the registry is being populated.
    All other methods to access models might raise an exception about the
    registry not being ready yet.
    Raises LookupError if model isn't found.
    """
    try:
        return apps.get_model(app_label, model_name)
    except AppRegistryNotReady:
        if apps.apps_ready and not apps.models_ready:
            # If this function is called while `apps.populate()` is
            # loading models, ensure that the module that defines the
            # target model has been imported and try looking the model up
            # in the app registry. This effectively emulates
            # `from path.to.app.models import Model` where we use
            # `Model = get_model('app', 'Model')` instead.
            app_config = apps.get_app_config(app_label)

            # `app_config.import_models()` cannot be used here because it
            # would interfere with `apps.populate()`.
            importlib.import_module('%s.%s' % (app_config.name, MODELS_MODULE_NAME))

            # In order to account for case-insensitivity of model_name,
            # look up the model through a private API of the app registry.
            return apps.get_registered_model(app_label, model_name)
        else:
            # This must be a different case (e.g. the model really doesn't
            # exist). We just re-raise the exception.
            raise


def random_string(length=6):
    code = uuid.uuid4().hex
    code = code.upper()[0:length]
    return code


def create_unique_id():
    return ''.join(random.choices(string.digits, k=8))


def choices_to_json(choices):
    to_dict = dict(choices)
    return json.dumps(to_dict, cls=LazyEncoder)


FONT_PATH = '{}/{}'.format(settings.MEDIA_ROOT, r'CircularStd-Bold.woff')
FONT_PATH_BLACK = '{}/{}'.format(settings.MEDIA_ROOT, r'CircularStd-Black.woff')
FONT_PATH_MEDIUM = '{}/{}'.format(settings.MEDIA_ROOT, r'CircularStd-Medium.woff')
CERTIFICATE_TEMPLATE = '{}/{}'.format(settings.MEDIA_ROOT, r'certificate-template.jpg')

FONT_FILE = ImageFont.truetype(FONT_PATH, 225)
FONT_FILE_DATE = ImageFont.truetype(FONT_PATH_MEDIUM, 65)
FONT_FILE_SCORE = ImageFont.truetype(FONT_PATH_BLACK, 95)
FONT_FILE_COURSE = ImageFont.truetype(FONT_PATH_BLACK, 90)
FONT_COLOR = '#194E9C'
FONT_COLOR_COURSE = '#DB2930'
WIDTH, HEIGHT = 3508, 2481

def make_cert(person_name=None, date_fmt=None, score=None, course_name=None, qrcode_text=None, instance=None):
    image_source = Image.open(CERTIFICATE_TEMPLATE)
    draw = ImageDraw.Draw(image_source)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=9,
        border=2,
    )

    qr.add_data(qrcode_text)
    qr.make(fit=False)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    qr_folder = '{}/{}/{}'.format(settings.MEDIA_ROOT, 'qrcode', slugify('qrcode-' + person_name + course_name) + '.jpg')
    qr_img.save(qr_folder)

    # Person name
    name_width, name_height = draw.textsize(person_name, font=FONT_FILE)
    draw.text((325, 1575), person_name, fill=FONT_COLOR, font=FONT_FILE)
    
    # Issue date
    date_width, date_height = draw.textsize(date_fmt, font=FONT_FILE_DATE)
    draw.text((325, 2150), date_fmt, fill=FONT_COLOR, font=FONT_FILE_DATE)

    # Score
    score_width, score_height = draw.textsize(score, font=FONT_FILE_SCORE)
    draw.text((3120, 2100), score, fill=FONT_COLOR, font=FONT_FILE_SCORE)

    # Course
    course_width, course_height = draw.textsize(course_name, font=FONT_FILE_COURSE)
    draw.text((325, 2035), course_name, fill=FONT_COLOR_COURSE, font=FONT_FILE_COURSE)

    certficiate_folder = '{}/{}/{}'.format(settings.MEDIA_ROOT, 'certificate', slugify(person_name + '-' + course_name) + '.jpg')
    image_source.paste(qr_img, (2760, 1555))
    image_source.save(certficiate_folder)

    return {
        'certificate': certficiate_folder,
        'qrcode': qr_folder,
    }
