# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from smartlicense.models import WalletID
from mcrpc import RpcClient
from django.conf import settings

class Command(BaseCommand):

    def handle(self, *args, **options):
        client = RpcClient(
            settings.NODE_IP, settings.NODE_PORT, settings.NODE_USER, settings.NODE_PWD
        )

        user_obj = User.objects.get(username='demo')
        addrs = client.getaddresses()
        for addr in addrs:
            print('Import WalletID:', addr)
            wid, created = WalletID.objects.get_or_create(owner=user_obj, address=addr)
            if created:
                print('Imported WalletID:', wid)
            else:
                print(wid, 'already exists.')



        # username, email = "demo", "demo@sample.org"
        # password = 'demo'
        # if User.objects.count() == 0:
        #     print("  Creating demo account user: '%s', passowrd '%s'" % (username, password))
        #     User.objects.create_superuser(username, email, password)
        # else:
        #     print("  Demo account can only be initialized if no Accounts exist")
