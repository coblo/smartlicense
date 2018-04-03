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
            ident='CCGHPBbk4QdBe-CYDfTq7Qc7Fre-CDh996KkRgC34-CRLdd9g4BSUyY',
            title="Image of Cat",
            name=fname,
            file=UploadedFile(open(path, 'rb')),
            txid='60398ad4534713ae66e179f70fc06d0f7d76d15fbef840a319b1ee4a041704ad'
        )
