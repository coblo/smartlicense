# -*- coding: utf-8 -*-
import uuid
from io import BytesIO
from os.path import splitext
from hashlib import sha256

import os

import docx2txt
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
import iscc
from martor.models import MartorField

from smartlicense.utils import get_client
from smartlicense.validators import validate_address


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
        return '{} - {}'.format(self.owner, self.address)


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

    tophash = models.CharField(
        verbose_name='tophash',
        max_length=64,
        blank=True,
        default=''
    )

    txid = models.CharField(
        verbose_name='Transaction-ID',
        help_text='Blockchain TX-ID of registered ISCC',
        max_length=64,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Media Content'
        verbose_name_plural = 'Media Contents'

    def __str__(self):
        return self.title

    def natural_key(self):
        return str(self)

    def register(self):
        # Register ISCC
        data = {
            'json': {
                'title': self.title,
                'tophash': self.tophash,
            }
        }
        if self.extra:
            data['json']['extra'] = self.extra

        client = get_client()
        txid = client.publish(
            settings.STREAM_ISCC,
            key_or_keys=list(self.ident.split('-')),
            data_hex_or_data_obj=data
        )
        return txid

    def clean(self):
        super().clean()
        if self.txid:
            raise ValidationError('Cannot change registered entry')
        if not self.pk and self.file:
            if not self.file.name.lower().endswith(self.ALLOWED_EXTENSIONS):
                raise ValidationError('Please provide a supported format: {}'.format(
                    self.ALLOWED_EXTENSIONS))
            basename, ext = os.path.splitext(self.file.name)
            # Store original file name
            self.name = self.file.name
            # Save with sanitized uuid as filename
            self.file.name = u''.join([str(uuid.uuid4()), ext.lower()])

    def save(self, *args, **kwargs):
        mid, title, extra = iscc.meta_id(self.title, self.extra)
        if self.ident:
            new_ident = [mid] + list(self.ident.split('-')[1:])
            self.ident = '-'.join(new_ident)
        if self.file:
            new_upload = isinstance(self.file.file, UploadedFile)
            if new_upload:
                # Generate ISCC

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
                iid, self.tophash = iscc.instance_id(data)
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

    class Meta:
        verbose_name = 'Transaction Model'
        verbose_name_plural = 'Transaction Models'

    def __str__(self):
        return self.ident


class RighsModuleQuerySet(models.QuerySet):

    def grants(self):
        return self.filter(type=RightsModule.GRANT)

    def restrictions(self):
        return self.filter(type=RightsModule.RESTRICTION)

    def obligations(self):
        return self.filter(type=RightsModule.OBLIGATION)


class SmartLicenseQuerySet(models.QuerySet):

    def tokenized(self):
        return self.filter(transaction_model=ActivationMode.TOKEN)

    def attestable(self):
        return self.filter(transaction_model=ActivationMode.ATTESTATION)

    def payable(self):
        return self.filter(transaction_model=ActivationMode.PAYMENT)


class RightsModule(models.Model):

    ADAPT = 'ADAPT'
    REPRODUCE = 'REPRODUCE'
    RESALE = 'RESALE'
    SHARE = 'SHARE'
    NON_COMMERCIAL = 'NON_COMMERCIAL'
    ATTRIBUTION = 'ATTRIBUTION'
    INDICATE_ADAPTIONS = 'INDICATE_ADAPTIONS'
    NO_INDUSTRIAL_PROPERTY = 'NO_INDUSTRIAL_PROPERTY'

    RIGHTS_MODULES = (
        (ADAPT, 'ADAPT (Grant)'),
        (REPRODUCE, 'REPRODUCE (Grant)'),
        (RESALE, 'RESALE (Grant)'),
        (SHARE, 'SHARE (Grant)'),
        (ATTRIBUTION, 'ATTRIBUTION (Obligation)'),
        (INDICATE_ADAPTIONS, 'INDICATE_ADAPTIONS (Obligation)'),
        (NON_COMMERCIAL, 'NON_COMMERCIAL (Restriction)'),
        (NO_INDUSTRIAL_PROPERTY, 'NO_INDUSTRIAL_PROPERTY (Restiction)')
    )

    GRANT, RESTRICTION, OBLIGATION = 'grant', 'restriction', 'obligation'

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

    short_code = models.CharField(
        max_length=2,
        verbose_name='Short Code',
        help_text='Short two letter code for Rights Module',
        default='',
    )

    help = models.CharField(
        max_length=255,
        help_text='Short Human readable definition',
        blank=True
    )

    legal_code = MartorField(
        help_text='Legal text for Smart License',
        blank=True,
    )

    objects = RighsModuleQuerySet.as_manager()

    class Meta:
        verbose_name = 'Rights Module'
        verbose_name_plural = 'Rights Modules'

    def __str__(self):
        return '{} ({})'.format(self.ident, self.type)


class Template(models.Model):

    code = models.CharField(
        max_length=16,
        verbose_name='Code',
        help_text='A short code (16 chars) as identifier for the template.',
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
        help_text="The tamplate data itself (Markdown/Jinja).",
    )

    class Meta:
        verbose_name = "Smart License Template"
        verbose_name_plural = "Smart License Templates"

    def __str__(self):
        return self.name


class SmartLicense(models.Model):

    ident = models.UUIDField(
        verbose_name='Smart License ID',
        help_text='Identifier of this specific SmartLicense offer',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    info = models.CharField(
        verbose_name='Public Info',
        help_text='A short public description about the Smart License. '
                  'Will also be added as info to tokens.',
        max_length=255,
        blank=False
    )

    template = models.ForeignKey(
        'smartlicense.Template',
        verbose_name='License Template',
        help_text='The contract template for the SmartLicense.',
        on_delete=models.CASCADE,
    )

    licensor = models.ForeignKey(
        'smartlicense.WalletID',
        verbose_name='Licensor',
        help_text='Wallet-ID of licensor. By default the stream '
                  'publisher Wallet-ID is assumed to be the '
                  'licensor. This assumption can be overridden by '
                  'providing an explicit list of one or more Wallet-IDs. '
                  'Future extensibility: licensor_identifier_type.',
        on_delete=models.CASCADE
    )

    material = models.ForeignKey(
        'smartlicense.MediaContent',
        verbose_name='Licensed Material',
        help_text='The materials to be licensed by this SmartLicense',
        related_name='material_smartlicenses',
        on_delete=models.CASCADE
    )

    transaction_model = models.ForeignKey(
        'smartlicense.ActivationMode',
        verbose_name='Transaction Model',
        help_text='Transaction Model accepted by the SmartLicense. If no '
                  'Transaction Model is given the SmartLicense is purely '
                  'informational and there is no defined way to close a '
                  'license contract on-chain.',
        related_name='+',
        blank=True,
        on_delete=models.CASCADE
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

    txid = models.CharField(
        verbose_name='Transaction-ID',
        help_text='Blockchain TX-ID of published Smart License',
        max_length=64,
        blank=True,
        default=''
    )

    objects = SmartLicenseQuerySet.as_manager()

    class Meta:
        verbose_name = "Smart License"
        verbose_name_plural = "Smart Licenses"

    def __str__(self):
        return self.info

    def get_absolute_url(self):
        return '/smartlicense/%s/' % self.ident

    def to_primitive(self):
        """Return python dict for stream publishing"""
        data = dict(
            template=sha256(self.template.template.encode('utf-8')).hexdigest(),
            rights_modules=list(self.rights_modules.values_list('ident', flat=True)),
            transaction_models=[self.transaction_model.ident],
        )
        wrapped = {'json': data}
        return wrapped

    def register(self, save=False):
        client = get_client()
        keys = [str(self.ident), self.material.ident]
        txid = client.publishfrom(
            self.licensor.address,
            settings.STREAM_SMART_LICENSE,
            keys,
            self.to_primitive()
        )

        # Create token if tokenize transaction model
        if self.transaction_model.ident == ActivationMode.TOKEN:
            client.issue(
                address=self.licensor.address,
                asset_name_or_asset_params={
                    'name': self.ident.bytes.hex(),
                    'open': True
                },
                quantity=1000,
                smallest_unit=1,
                native_amount=0.1,
                custom_fields={
                    'info': self.info,
                    'type': 'smart-license'
                }
            )
        if save:
            self.txid = txid
            self.save()
        return txid


class Attestation(models.Model):

    smart_license = models.ForeignKey(
        SmartLicense,
        verbose_name='Smart License',
        help_text='Choose Smart License to create an attestation for.',
        on_delete=models.CASCADE
    )

    licensee = models.CharField(
        verbose_name='For',
        help_text='Walled-ID of user to whom you want to attest the Smart License',
        max_length=64,
        validators=[validate_address]
    )

    txid = models.CharField(
        verbose_name='Transaction-ID',
        help_text='Blockchain TX-ID of Attestation',
        max_length=64,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Attestation'
        verbose_name_plural = 'Attestations'

    def __str__(self):
        return 'Attestation ({})'.format(self.txid[:8])

    def register(self, save=False):
        client = get_client()
        smart_license_id = str(self.smart_license.ident)
        licensor = self.smart_license.licensor.address
        licensee = self.licensee
        data = {
            'json': {'licensee': licensee}
        }
        txid = client.publishfrom(
            from_address=licensor,
            stream_identifier=settings.STREAM_SMART_LICENSE,
            key_or_keys=['ATT', smart_license_id],
            data_hex_or_data_obj=data
        )
        if save:
            self.txid = txid
            self.save()
        return txid

    def save(self, *args, **kwargs):
        if not self.txid:
            self.txid = self.register(save=False)
        super().save(*args, **kwargs)


class TokenTransaction(models.Model):

    smart_license = models.ForeignKey(
        SmartLicense,
        verbose_name='Smart License',
        help_text='Choose Smart License for which you want to send a Token',
        on_delete=models.CASCADE
    )

    recipient = models.CharField(
        verbose_name='Recipient',
        help_text='Walled-ID of user to whom you want to send the Smart License Token',
        max_length=64,
        validators=[validate_address]
    )

    txid = models.CharField(
        verbose_name='Transaction-ID',
        help_text='Blockchain TX-ID of token transaction',
        max_length=64,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Token Transaction'
        verbose_name_plural = 'Token Transactions'

    def register(self):
        client = get_client()
        token_name = self.smart_license.ident.bytes.hex()
        txid = client.sendasset(
            address=self.recipient,
            asset_identifier=token_name,
            asset_qty=1,
            native_amount=0.1
        )
        return txid

    def save(self, *args, **kwargs):
        if not self.txid:
            self.txid = self.register()
        super(TokenTransaction, self).save(*args, **kwargs)
