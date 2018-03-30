# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models import TextField
from django.utils.safestring import mark_safe
from django_object_actions import DjangoObjectActions, \
    takes_instance_or_queryset
from martor.widgets import AdminMartorWidget

from smartlicense.models import (
    WalletID,
    SmartLicense,
    ActivationMode,
    RightsModule,
    Template,
    MediaContent,
    Attestation, TokenTransaction)


admin.site.site_header = 'Smart License Demo'
admin.site.site_title = 'Smart License Demo'
admin.site.index_title = ''
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.disable_action('delete_selected')

# admin.site.login_template = 'login.html'


@admin.register(WalletID)
class WalletIDAdmin(admin.ModelAdmin):
    list_display = 'address', 'memo', 'owner'
    fields = 'owner', 'address', 'memo'
    readonly_fields = 'owner', 'address'
    search_fields = ('user__username', 'address')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SmartLicense)
class SmartLicenseAdmin(DjangoObjectActions, admin.ModelAdmin):

    list_display = ('ident', 'memo', 'licensor', 'template', 'material', 'admin_published')
    fieldsets = (
        ('Basics', {
            'fields': ('ident', 'info', 'memo', 'template', 'licensor', 'material'),
        }),
        ('SmartLicense Settings', {
            'fields': ('transaction_model', 'rights_modules'),
        }),
        ('Blockchain Info', {
            'fields': ('admin_txid',)
        })
    )
    readonly_fields = ('ident', 'admin_txid')
    autocomplete_fields = ('rights_modules', )

    change_actions = ('publish',)

    def admin_licensors(self, obj):
        return ','.join(obj.licensors.values_list('owner__username', flat=True))
    admin_licensors.short_description = 'Licensor(s)'

    def admin_materials(self, obj):
        return ','.join(obj.materials.values_list('title', flat=True))
    admin_materials.short_description = 'Licensed Content'

    def admin_txid(self, obj):
        if obj.txid:
            url = 'http://explorer.coblo.net/tx/{}?raw'.format(obj.txid)
            link = '<a href={} target="_blank">{}</a>'.format(url, obj.txid)
            return mark_safe(link)
    admin_txid.short_description = 'Transaction-ID'

    def admin_published(self, obj):
        return bool(obj.txid)
    admin_published.boolean = True
    admin_published.short_description = 'Published'

    def publish(self, request, obj):
        if not obj.txid:
            obj.publish(save=True)
    publish.label = 'Publish'
    publish.short_description = 'Publish Smart License Offer to Content Blockchain'


@admin.register(ActivationMode)
class ActivationModeAdmin(admin.ModelAdmin):
    list_display = ('ident', 'description',)
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass


@admin.register(RightsModule)
class RightsModuleAdmin(admin.ModelAdmin):
    list_display = 'short_code', 'ident', 'help', 'type'
    fields = ('ident', 'short_code', 'type', 'help', 'legal_code',)
    list_editable = ('type',)
    search_fields = ('ident', 'help')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = 'code', 'name', 'description'
    actions = None
    fieldsets = [
        ('', {'fields': ('code', 'name', 'description')}),
        ('Body', {'classes': ('full-width',), 'fields': ('template',)})
    ]

    # formfield_overrides = {
    #     TextField: {'widget': AdminMartorWidget},
    # }

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass


@admin.register(MediaContent)
class MediaContentAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('title', 'name',  'ident', 'extra', 'admin_registered')
    fields = ('ident', 'title', 'extra', 'file', 'admin_txid')
    readonly_fields = 'ident', 'admin_txid'
    search_fields = ('title', 'name')
    actions = ['action_register']
    change_actions = ['action_register']
    # changelist_actions = ['action_register']

    def admin_txid(self, obj):
        if obj.txid:
            url = 'http://explorer.coblo.net/tx/{}?raw'.format(obj.txid)
            link = '<a href={} target="_blank">{}</a>'.format(url, obj.txid)
            return mark_safe(link)
    admin_txid.short_description = 'Transaction-ID'

    def admin_registered(self, obj):
        return bool(obj.txid)
    admin_registered.boolean = True
    admin_registered.short_description = 'Registered'

    @takes_instance_or_queryset
    def action_register(self, request, queryset):
        for obj in queryset:
            if not obj.txid:
                txid = obj.register()
                obj.txid = txid
                obj.save()
    action_register.label = 'Register on Blockchain'
    action_register.short_description = 'Register on Content Blockchain ISCC-Stream'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True


@admin.register(Attestation)
class AttestationAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = 'smart_license', 'licensee', 'admin_published'
    readonly_fields = 'admin_txid',

    change_actions = ('publish',)

    def publish(self, request, obj):
        if not obj.txid:
            obj.publish(save=True)
    publish.label = 'Publish'
    publish.short_description = 'Publish Attestation to Content Blockchain'

    def admin_published(self, obj):
        return bool(obj.txid)
    admin_published.boolean = True
    admin_published.short_description = 'Published'

    def admin_txid(self, obj):
        if obj.txid:
            url = 'http://explorer.coblo.net/tx/{}?raw'.format(obj.txid)
            link = '<a href={} target="_blank">{}</a>'.format(url, obj.txid)
            return mark_safe(link)
    admin_txid.short_description = 'Transaction-ID'


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    list_display = 'smart_license', 'recipient',
    fields = 'smart_license', 'recipient', 'admin_txid'
    readonly_fields = 'admin_txid',

    def admin_txid(self, obj):
        if obj.txid:
            url = 'http://explorer.coblo.net/tx/{}?raw'.format(obj.txid)
            link = '<a href={} target="_blank">{}</a>'.format(url, obj.txid)
            return mark_safe(link)
    admin_txid.short_description = 'Transaction-ID'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True
