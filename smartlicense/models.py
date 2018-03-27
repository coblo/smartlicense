# -*- coding: utf-8 -*-
import uuid
import hashlib
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.conf import settings


class WalletID(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text='Owner of Wallet-ID',
        on_delete=models.CASCADE,
    )

    address = models.CharField(
        help_text='Wallet address',
        max_length=60,

    )

    class Meta:
        verbose_name = 'Wallet-ID'
        verbose_name_plural = 'Wallet-IDs'

    def __str__(self):
        return '{} ({}...)'.format(self.owner, self.address[:6])

class MediaContent(models.Model):

    ISCC, ISBN, SHA256 = 'iscc', 'isbn', 'sha256'

    TYPE_CHOICES = (
        (ISCC, 'Iscc'),
        (ISBN, 'Isbn'),
        (SHA256, 'SHA256')
    )

    ident = models.CharField(
        verbose_name='Content Identifier',
        max_length=64,
        blank=True
    )

    ident_type = models.CharField(
        verbose_name='Content Identifier Type',
        choices=TYPE_CHOICES,
        max_length=8,
        default=SHA256
    )

    title = models.CharField(
        verbose_name='Content Title',
        max_length=256,
        blank=False,
    )

    file = models.FileField(
        verbose_name='Media Content File',
        upload_to='mediafiles',
        blank=False,
    )

    class Meta:
        verbose_name = 'Media Content'
        verbose_name_plural = 'Media Contents'
        unique_together = ('ident', 'ident_type',)

    def __str__(self):
        return self.title

    def natural_key(self):
        return str(self)

    def get_sha256(self):
        sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            sha256.update(chunk)
        return sha256.hexdigest().upper()

    def save(self, *args, **kwargs):
        if self.file:
            sha256 = self.get_sha256()
            new_upload = isinstance(self.file.file, UploadedFile) or self.ident != sha256
            if new_upload:
                self.ident = sha256
        super().save(*args, *kwargs)


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
    name = models.CharField(max_length=64)
    template = models.TextField()

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
