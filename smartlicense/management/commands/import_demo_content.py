# -*- coding: utf-8 -*-
from django.core.files.uploadedfile import UploadedFile
from django.core.management import BaseCommand
from os.path import join

from smartlicense.models import MediaContent

from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        fname = 'testimage.jpg'
        path = join(settings.BASE_DIR, 'smartlicense', 'fixtures', fname)
        print('Import demo content:', path)
        MediaContent.objects.get_or_create(
            title="Image of Cat",
            name=fname,
            file=UploadedFile(open(path, 'rb'))
        )
