# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from smartlicense.utils import get_client


def validate_address(value):
    client = get_client()
    result = client.validateaddress(value)
    if result.get('isvalid') is False:
        raise ValidationError(
            _('%(value)s is not a valid address'),
            params={'value': value},
        )
