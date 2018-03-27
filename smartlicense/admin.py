# -*- coding: utf-8 -*-
from django.contrib import admin

from smartlicense.models import (
    WalletID,
    SmartLicense,
    ActivationMode,
    RightsModule,
    Template,
    MediaContent,
)


admin.site.site_header = 'SmartLicense Demo'
admin.site.site_title = 'SmartLicense Demo'


@admin.register(WalletID)
class WalletIDAdmin(admin.ModelAdmin):
    list_display = 'owner', 'address'
    fields = 'owner', 'address'
    search_fields = ('user__username', 'address')


@admin.register(SmartLicense)
class SmartLicenseAdmin(admin.ModelAdmin):

    list_display = ('ident', 'admin_licensors', 'template', 'admin_materials')
    fieldsets = (
        ('Basics', {
            'fields': ('ident', 'template', 'licensors', 'materials'),
        }),
        ('SmartLicense Settings', {
            'fields': ('activation_modes', 'rights_modules'),
        }),
    )
    readonly_fields = ('ident',)
    autocomplete_fields = (
        'licensors', 'materials', 'activation_modes', 'rights_modules')

    def admin_licensors(self, obj):
        return ','.join(obj.licensors.values_list('owner__username', flat=True))
    admin_licensors.short_description = 'Licensor(s)'

    def admin_materials(self, obj):
        return ','.join(obj.materials.values_list('title', flat=True))
    admin_materials.short_description = 'Licensed Content'


@admin.register(ActivationMode)
class ActivationModeAdmin(admin.ModelAdmin):
    list_display = ('ident', 'description',)
    search_fields = ('ident',)


@admin.register(RightsModule)
class RightsModuleAdmin(admin.ModelAdmin):
    list_display = ('ident', 'help', 'type')
    fields = ('ident', 'type', 'help', 'legal_definition', 'legal_code',)
    list_editable = ('type',)
    # readonly_fields = ('ident', )

    search_fields = ('ident', 'help')


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'natural_key',)
    fields = ('ident', 'ident_type', 'title', 'file')
    readonly_fields = ('ident', 'ident_type')

    search_fields = ('title',)