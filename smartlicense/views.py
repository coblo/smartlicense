# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template import Template, Context
import markdown

from smartlicense.models import SmartLicense, RightsModule
from smartlicense.models import Template as SMTemplate


def smartlicense_detail(request, ident):
    sm_obj = SmartLicense.objects.get(ident=ident)
    return render(request, 'smartlicense.html', {'sm': sm_obj})


def rights_profile_detail(request, codes):
    codes = [code.upper() for code in codes.split('-')]
    rights_modules = RightsModule.objects.filter(short_code__in=codes)
    tpl = SMTemplate.objects.first()
    template = Template(tpl.template)
    context = Context({'rights_modules': rights_modules,})
    data = template.render(context)
    inner_html = markdown.markdown(data, extensions=['markdown.extensions.abbr'])
    outer_context = {'content': inner_html}
    return render(request, 'rights_profile.html', outer_context)
