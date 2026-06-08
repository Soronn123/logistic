from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Ticket, TicketMessage, Transaction


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'phone', 'role', 'is_company', 'balance', 'is_active']
    list_filter = ['role', 'is_company', 'is_active', 'theme', 'language']
    search_fields = ['email', 'username', 'phone', 'company_name', 'inn']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Company'), {'fields': ('is_company', 'company_name', 'inn')}),
        (_('Preferences'), {'fields': ('language', 'theme')}),
        (_('Role & Balance'), {'fields': ('role', 'balance')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ['sender', 'message', 'created_at', 'is_internal_note']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'status', 'priority', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['subject', 'created_by__email']
    inlines = [TicketMessageInline]
    raw_id_fields = ['created_by', 'assigned_to']


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'sender', 'created_at', 'is_internal_note']
    list_filter = ['is_internal_note']
    search_fields = ['message', 'sender__email']
    readonly_fields = ['ticket', 'sender', 'message', 'created_at']

    def has_add_permission(self, request):
        return False


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'balance_after', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['user__email', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['user', 'amount', 'transaction_type', 'description', 'created_at', 'balance_after']

    def has_add_permission(self, request):
        return False
