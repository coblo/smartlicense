# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset


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


class RegisterableMixin(DjangoObjectActions):

    actions = ['action_register']
    change_actions = ['action_register']

    @takes_instance_or_queryset
    def action_register(self, request, queryset):
        for obj in queryset:
            if not obj.txid:
                txid = obj.register()
                obj.txid = txid
                obj.save()
    action_register.label = 'Register on Blockchain'
    action_register.short_description = 'Register on Content Blockchain'

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
class SmartLicenseAdmin(RegisterableMixin, admin.ModelAdmin):

    list_display = ('ident', 'info', 'licensor', 'template', 'material', 'admin_registered')
    fieldsets = (
        ('Basics', {
            'fields': ('ident', 'template', 'material', 'info', 'licensor'),
        }),
        ('SmartLicense Settings', {
            'fields': ('transaction_model', 'rights_modules'),
        }),
        ('Blockchain Info', {
            'fields': ('admin_txid',)
        })
    )

    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    readonly_fields = ('ident', 'admin_txid')


@admin.register(ActivationMode)
class ActivationModeAdmin(admin.ModelAdmin):
    list_display = ('ident', 'description',)
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # def save_model(self, request, obj, form, change):
    #     pass


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
class MediaContentAdmin(RegisterableMixin, admin.ModelAdmin):
    list_display = ('title', 'name',  'ident', 'extra', 'admin_registered')
    fields = ('ident', 'title', 'extra', 'file', 'admin_txid')
    readonly_fields = 'ident', 'admin_txid'
    search_fields = ('title', 'name')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True


@admin.register(Attestation)
class AttestationAdmin(RegisterableMixin, admin.ModelAdmin):
    list_display = 'smart_license', 'licensee', 'admin_registered'
    fields = 'smart_license', 'licensee', 'admin_txid'
    readonly_fields = 'admin_txid',

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only attestable Smart Licenses selectable"""
        if db_field.name == "smart_license":
            kwargs["queryset"] = SmartLicense.objects.attestable()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TokenTransaction)
class TokenTransactionAdmin(RegisterableMixin, admin.ModelAdmin):
    list_display = 'smart_license', 'recipient', 'admin_registered'
    fields = 'smart_license', 'recipient', 'admin_txid'
    readonly_fields = 'admin_txid',

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only tokenized Smart Licenses selectable"""
        if db_field.name == "smart_license":
            kwargs["queryset"] = SmartLicense.objects.tokenized()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True
