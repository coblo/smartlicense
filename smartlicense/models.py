# -*- coding: utf-8 -*-
import uuid
from io import BytesIO
from os.path import splitext

import os

import docx2txt
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
import iscc
from martor.models import MartorField


class WalletID(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text='Owner of Wallet-ID',
        on_delete=models.CASCADE,
    )

    address = models.CharField(
        verbose_name='Wallet-ID',
        help_text='A valid blockchain wallet address.',
        max_length=60,
    )

    memo = models.CharField(
        max_length=255,
        verbose_name='Internal Memo',
        help_text='Short internal note about this address.',
        blank=True
    )

    class Meta:
        verbose_name = 'Wallet-ID'
        verbose_name_plural = 'Wallet-IDs'

    def __str__(self):
        return '{} ({}...)'.format(self.owner, self.address[:6])


class MediaContent(models.Model):

    IMAGE_EXTENSIONS = ('jpg', 'png',)
    TEXT_EXTENSIONS = ('txt', 'docx')
    ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS + TEXT_EXTENSIONS

    ident = models.CharField(
        verbose_name='ISCC',
        max_length=55,
        blank=True,
    )

    title = models.CharField(
        verbose_name='Content Title',
        max_length=128,
        blank=False,
    )

    extra = models.CharField(
        verbose_name='Extra Info',
        max_length=128,
        blank=True,
        default="",
    )

    file = models.FileField(
        verbose_name='Media Content File',
        help_text='Supported file types: {}'.format(ALLOWED_EXTENSIONS),
        upload_to='mediafiles',
        blank=False,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS),
        ],
    )

    name = models.CharField(
        verbose_name='Filename',
        max_length=255,
    )

    class Meta:
        verbose_name = 'Media Content'
        verbose_name_plural = 'Media Contents'

    def __str__(self):
        return self.title

    def natural_key(self):
        return str(self)

    def clean(self):
        super().clean()
        if not self.pk and self.file:
            if not self.file.name.lower().endswith(self.ALLOWED_EXTENSIONS):
                raise ValidationError('Please provide a supported format: {}'.format(self.ALLOWED_EXTENSIONS))
            basename, ext = os.path.splitext(self.file.name)
            # Store original file name
            self.name = self.file.name
            # Save with sanitized uuid as filename
            self.file.name = u''.join([str(uuid.uuid4()), ext.lower()])

    def save(self, *args, **kwargs):
        if self.file:
            new_upload = isinstance(self.file.file, UploadedFile)
            if new_upload:
                mid, title, extra = iscc.meta_id(self.title, self.extra)
                filename, file_extension = splitext(self.file.name)
                ext = file_extension.lower().lstrip('.')
                data = self.file.open('rb').read()
                if ext in self.TEXT_EXTENSIONS:
                    if ext == 'docx':
                        text = docx2txt.process(BytesIO(data))
                        print(text)
                    else:
                        text = self.file.open().read()
                    cid = iscc.content_id_text(text)
                elif ext in self.IMAGE_EXTENSIONS:
                    cid = iscc.content_id_image(BytesIO(data))
                did = iscc.data_id(data)
                iid, tophash = iscc.instance_id(data)
                iscc_code = '-'.join((mid, cid, did, iid))
                self.ident = iscc_code
        super(MediaContent, self).save(*args, **kwargs)


class ActivationMode(models.Model):

    PAYMENT = 'PAYMENT'
    ATTESTATION = 'ATTESTATION'
    TOKEN = 'TOKEN'

    ACTIVATION_MODES = (
        (PAYMENT, 'On-chain Payment'),
        (ATTESTATION, 'On-chain Attestation'),
        (TOKEN, 'On-chain Tokenization'),
    )

    ident = models.CharField(primary_key=True, choices=ACTIVATION_MODES, max_length=24)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.ident


class RighsModuleManager(models.Manager):

    def grants(self):
        return self.filter(type=RightsModule.GRANT)

    def restrictions(self):
        return self.filter(type=RightsModule.RESTRICTION)

    def oblications(self):
        return self.filter(type=RightsModule.OBLIGATION)


class RightsModule(models.Model):

    ADAPT = 'ADAPT'
    LEND = 'LEND'
    REPRODUCE = 'REPRODUCE'
    RESALE = 'RESALE'
    SHARE = 'SHARE'
    NON_COMMERCIAL = 'NON_COMERCIAL'
    ATTRIBUTION = 'ATTRIBUTION'
    INDICATE_ADAPTIONS = 'INDICATE_ADAPTIONS'

    RIGHTS_MODULES = (
        (ADAPT, 'ADAPT'),
        (LEND, 'LEND'),
        (REPRODUCE, 'REPRODUCE'),
        (RESALE, 'RESALE'),
        (SHARE, 'SHARE'),
        (ATTRIBUTION, 'ATTRIBUTION'),
        (INDICATE_ADAPTIONS, 'INDICATE_ADAPTIONS'),
        (NON_COMMERCIAL, 'NON_COMERCIAL')
    )

    GRANT, RESTRICTION, OBLIGATION = 'grant', 'restriction', 'oblication'

    RIGHTS_MODULE_TYPES = (
        (GRANT, 'Grants right'),
        (RESTRICTION, 'Resticts right'),
        (OBLIGATION, 'Requires obligation')
    )

    ident = models.CharField(
        help_text='Rights Module Identifier',
        primary_key=True,
        choices=RIGHTS_MODULES,
        max_length=64
    )

    type = models.CharField(
        help_text='The Type of this Rights Module',
        choices=RIGHTS_MODULE_TYPES,
        max_length=16,
        blank=True,
        default=GRANT,
    )

    help = models.TextField(
        help_text='Human readable definition',
        blank=True
    )

    legal_definition = models.TextField(
        help_text='Legal definition',
        blank=True
    )

    legal_code = models.TextField(
        help_text='Legal text for SmartLicense',
        blank=True,
    )

    objects = RighsModuleManager()

    class Meta:
        verbose_name = 'Rights Module'
        verbose_name_plural = 'Rights Modules'

    def __str__(self):
        return self.ident


class Template(models.Model):

    code = models.CharField(
        max_length=8,
        verbose_name='Code',
        help_text='A short code (8 chars) as identifier for the template.',
        unique=True
    )

    name = models.CharField(
        max_length=64,
        verbose_name='Name',
        help_text="A human readable title for the Smart License template."
    )

    description = models.CharField(
        max_length=255,
        verbose_name='Description',
        help_text="A short description of Smart License template."
    )

    template = MartorField(
        verbose_name='Template',
        help_text="The tamplate data itself (Markdown/Jinja)."
    )

    class Meta:
        verbose_name = "Smart License Template"
        verbose_name_plural = "Smart License Templates"

    def __str__(self):
        return self.name


class SmartLicense(models.Model):

    ident = models.UUIDField(
        verbose_name='Identifier',
        help_text='Identifier of this specific SmartLicense offer',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    template = models.ForeignKey(
        'smartlicense.Template',
        help_text='The contract template for the SmartLicense.',
        on_delete=models.CASCADE,
    )

    licensors = models.ManyToManyField(
        'smartlicense.WalletID',
        verbose_name='Licensor(s)',
        help_text='Wallet-ID(s) of licensor(s). By default the stream '
                  'publisher(s) Wallet-ID(s) are assumed to be the '
                  'licensor(s). This assumption can be overridden by '
                  'providing an explicit list of one or more Wallet-IDs. '
                  'Future extensibility: licensor_identifier_type.',
        related_name='wallet_id_smartlicenses',
        blank=True,
    )

    materials = models.ManyToManyField(
        'smartlicense.MediaContent',
        help_text='The materials to be licensed by this SmartLicense',
        related_name='material_smartlicenses',
    )

    activation_modes = models.ManyToManyField(
        'smartlicense.ActivationMode',
        help_text='ActivationModes accepted by the SmartLicense. If no '
                  'ActivationMode is given the SmartLicense is purely '
                  'informational and there is no defined way to close a '
                  'license contract on-chain.',
        related_name='+',
        blank=True
    )

    rights_modules = models.ManyToManyField(
        'smartlicense.RightsModule',
        verbose_name='Rights Modules',
        help_text='List of Rights Modules to be effective for this '
                  'SmartLicense. If no RightsModules are provided only the '
                  'general, non-optional clauses of the SmartLicense will be '
                  'effective.',
        related_name='+',
    )

    class Meta:
        verbose_name = "Smart License"
        verbose_name_plural = "Smart Licenses"

    def get_absolute_url(self):
        return '/smartlicense/%s/' % self.ident
