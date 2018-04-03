# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template import Template, Context
import markdown
from easy_pdf.rendering import render_to_pdf_response

from smartlicense.models import SmartLicense, RightsModule
from smartlicense.models import Template as SMTemplate


def smartlicense_detail(request, ident):
    sl_obj = SmartLicense.objects.get(ident=ident)
    tpl = SMTemplate.objects.first()
    template = Template(tpl.template)
    context = Context({'rights_modules': sl_obj.rights_modules.all()})
    data = template.render(context)
    inner_html = markdown.markdown(data, extensions=['markdown.extensions.abbr'])
    outer_context = {'content': inner_html, 'sl': sl_obj}
    return render(request, 'sl.html', outer_context)


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


def rights_profile_pdf(request, codes):
    codes = [code.upper() for code in codes.split('-')]
    rights_modules = RightsModule.objects.filter(short_code__in=codes)
    tpl = SMTemplate.objects.first()
    template = Template(tpl.template)
    context = Context({'rights_modules': rights_modules,})
    data = template.render(context)
    inner_html = markdown.markdown(data, extensions=['markdown.extensions.abbr'])
    outer_context = {'content': inner_html}
    return render_to_pdf_response(request, 'rights_profile_pdf.html', outer_context)
