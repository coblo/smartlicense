# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from smartlicense.models import WalletID
from smartlicense.utils import get_client


class Command(BaseCommand):

    def handle(self, *args, **options):
        client = get_client()

        user_obj = User.objects.get(username='demo')
        addrs = client.getaddresses()
        for addr in addrs:
            print('Import WalletID:', addr)
            wid, created = WalletID.objects.get_or_create(owner=user_obj, address=addr)
            if created:
                print('Imported WalletID:', wid)
            else:
                print(wid, 'already exists.')
