# -*- coding: utf-8 -*-
from django.shortcuts import render
from smartlicense.models import SmartLicense


def smartlicense_detail(request, ident):
    sm_obj = SmartLicense.objects.get(ident=ident)
    return render(request, 'smartlicense.html', {'sm': sm_obj})
