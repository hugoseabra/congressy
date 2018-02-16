# noinspection PyPep8
import os

import django

django.setup()

from gatheros_event.models import Event
from django.core.files import File

BIN_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_PATH = os.path.dirname(os.path.dirname(BIN_PATH))

IMAGE_DIR_PATH = os.path.join(
    BASE_PATH,
    'fixtures',
    'workflows',
    'media',
    'nego_borel_amnesia.jpg'
)

image_blob = open(IMAGE_DIR_PATH, 'rb')

# Saves fixtures image to test events
for event in Event.objects.all():
    event.info.image_main.save('nego_borel_amnesia.jpg', image_blob)
    event.save()
