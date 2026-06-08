from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderStatusHistory, OrderDocument


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'timestamp', 'comment']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class OrderDocumentInline(admin.TabularInline):
    model = OrderDocument
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'user', 'sender_name', 'recipient_name', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'service']
    search_fields = ['tracking_number', 'sender_name', 'sender_phone', 'recipient_name', 'recipient_phone', 'cargo_description']
    date_hierarchy = 'created_at'
    inlines = [OrderStatusHistoryInline, OrderDocumentInline]
    raw_id_fields = ['user', 'sender_address', 'recipient_address', 'service']
    readonly_fields = ['tracking_number', 'created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': ['tracking_number', 'user', 'status', 'total_price']}),
        (_('Sender'), {'fields': ['sender_name', 'sender_phone', 'sender_address', 'sender_address_detail']}),
        (_('Recipient'), {'fields': ['recipient_name', 'recipient_phone', 'recipient_address', 'recipient_address_detail']}),
        (_('Cargo'), {'fields': ['cargo_description', 'weight', 'volume', 'length', 'width', 'height', 'declared_value']}),
        (_('Service'), {'fields': ['service', 'additional_services']}),
        (_('Dates'), {'fields': ['estimated_delivery_date', 'actual_delivery_date', 'created_at', 'updated_at']}),
    ]


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'timestamp']
    list_filter = ['status']
    search_fields = ['order__tracking_number', 'comment']
    readonly_fields = ['order', 'status', 'changed_by', 'timestamp', 'comment']

    def has_add_permission(self, request):
        return False


@admin.register(OrderDocument)
class OrderDocumentAdmin(admin.ModelAdmin):
    list_display = ['order', 'document_type', 'uploaded_at']
    list_filter = ['document_type']
    search_fields = ['order__tracking_number', 'document_type']
