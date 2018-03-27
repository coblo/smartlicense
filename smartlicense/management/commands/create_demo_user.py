# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        username, email = "demo", "demo@sample.org"
        password = 'demo'
        if User.objects.count() == 0:
            print("  Creating demo account user: '%s', passowrd '%s'" % (username, password))
            User.objects.create_superuser(username, email, password)
        else:
            print("  Demo account can only be initialized if no Accounts exist")
