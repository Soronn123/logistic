from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PartnerApplication, Banner, IframeModule


@admin.register(PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_person', 'email', 'phone', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['company_name', 'contact_person', 'email', 'phone']
    readonly_fields = ['company_name', 'contact_person', 'email', 'phone', 'website', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    @admin.action(description=_('Approve selected applications'))
    def approve_applications(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description=_('Mark selected as reviewing'))
    def start_reviewing(self, request, queryset):
        queryset.update(status='reviewing')

    actions = [approve_applications, start_reviewing]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'placement', 'is_active', 'start_date', 'end_date', 'clicks_count']
    list_filter = ['placement', 'is_active']
    search_fields = ['title']


@admin.register(IframeModule)
class IframeModuleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']
