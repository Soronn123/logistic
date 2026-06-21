from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from .models import CargoTemplate, CompanyApplication, ContactTemplate, CustomUser, DeliveryTemplate, ManagerDirectoryPermission, Ticket, TicketMessage, Transaction


@admin.action(description=_('Close selected tickets'))
def close_tickets(modeladmin, request, queryset):
    queryset.update(status=Ticket.Status.CLOSED)


@admin.action(description=_('Reopen selected tickets'))
def reopen_tickets(modeladmin, request, queryset):
    queryset.update(status=Ticket.Status.OPEN)


@admin.action(description=_('Mark selected as in progress'))
def mark_in_progress(modeladmin, request, queryset):
    queryset.update(status=Ticket.Status.IN_PROGRESS)


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ['sender', 'created_at']
    can_delete = False
    fields = ['sender', 'message', 'is_internal_note', 'created_at']

    def has_change_permission(self, request, obj=None):
        return False

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if not obj.pk:
                obj.sender = request.user
                ticket = obj.ticket
                if ticket.status == Ticket.Status.CLOSED:
                    ticket.status = Ticket.Status.IN_PROGRESS
                    ticket.save()
            obj.save()
        formset.save_m2m()


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


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'status', 'priority', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['subject', 'created_by__email']
    inlines = [TicketMessageInline]
    raw_id_fields = ['created_by', 'assigned_to']
    actions = [close_tickets, reopen_tickets, mark_in_progress]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = True
        extra_context['show_save_and_add_another'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        opts = self.model._meta
        pk_value = obj.pk

        if '_close_ticket' in request.POST:
            obj.status = Ticket.Status.CLOSED
            obj.save(update_fields=['status'])
            self.message_user(request, _('Ticket closed.'))
            return HttpResponseRedirect(request.path)

        if '_reopen_ticket' in request.POST:
            obj.status = Ticket.Status.OPEN
            obj.save(update_fields=['status'])
            self.message_user(request, _('Ticket reopened.'))
            return HttpResponseRedirect(request.path)

        if '_mark_in_progress' in request.POST:
            obj.status = Ticket.Status.IN_PROGRESS
            obj.save(update_fields=['status'])
            self.message_user(request, _('Ticket marked as in progress.'))
            return HttpResponseRedirect(request.path)

        if '_assign_to_me' in request.POST:
            obj.assigned_to = request.user
            obj.save(update_fields=['assigned_to'])
            self.message_user(request, _('Ticket assigned to you.'))
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)


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


@admin.register(CargoTemplate)
class CargoTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'weight', 'declared_value', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__email', 'cargo_description']
    date_hierarchy = 'created_at'


@admin.register(ManagerDirectoryPermission)
class ManagerDirectoryPermissionAdmin(admin.ModelAdmin):
    list_display = ['manager', 'directory_display', 'can_access', 'updated_at']
    list_filter = ['directory', 'can_access', 'manager']
    search_fields = ['manager__email', 'manager__username']
    list_editable = ['can_access']
    autocomplete_fields = ['manager']
    date_hierarchy = 'updated_at'

    def directory_display(self, obj):
        return obj.get_directory_display()
    directory_display.short_description = _('Directory')
    directory_display.admin_order_field = 'directory'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'manager':
            kwargs['queryset'] = CustomUser.objects.filter(role='manager')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(CompanyApplication)
class CompanyApplicationAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'inn', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['company_name', 'inn', 'user__email']
    readonly_fields = ['user', 'company_name', 'inn', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    @admin.action(description=_('Approve selected applications'))
    def approve_applications(self, request, queryset):
        for app in queryset:
            user = app.user
            user.company_name = app.company_name
            user.inn = app.inn
            user.is_company = True
            user.save()
            app.status = 'approved'
            app.save()

    @admin.action(description=_('Mark selected as under review'))
    def start_reviewing(self, request, queryset):
        queryset.update(status='reviewing')

    @admin.action(description=_('Reject selected applications'))
    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')

    actions = [approve_applications, start_reviewing, reject_applications]
