# -*- coding: utf-8 -*-
from django.conf import settings
from mcrpc import RpcClient


def get_client():
    return RpcClient(
        settings.NODE_IP,
        settings.NODE_PORT,
        settings.NODE_USER,
        settings.NODE_PWD
    )
