from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Document, AccountingRequest


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'uploaded_at']
    list_filter = ['category', 'is_active', 'services', 'additional_services']
    search_fields = ['title', 'title_en', 'description']
    filter_horizontal = ['services', 'additional_services']


@admin.register(AccountingRequest)
class AccountingRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'document_type', 'period_start', 'period_end', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'document_type']
    readonly_fields = ['user', 'document_type', 'period_start', 'period_end', 'created_at', 'fulfilled_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False
